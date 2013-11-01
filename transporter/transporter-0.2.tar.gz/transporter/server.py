import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import watcher
import index
import os
import sys
import time
import diff_match_patch
from Queue import Empty
import cPickle as pickle
import signal
from Queue import Queue

from tornado.log import app_log as logger
import logging
logger.setLevel(logging.DEBUG)
logger.name = "server"

from transporter.actions import Actions

class ServerEventListener(object):
    def __init__(self, server):
        self.server = server

    def on_moved(self, event):
        what = 'directory' if event.is_directory else 'file'
        logger.info("Moved %s: from %s to %s", what, event.src_path,
                 event.dest_path)

    def on_created(self, event):

        if '.kd-cache' in event.src_path:
            return

        what = 'directory' if event.is_directory else 'file'
        logger.info("Created %s: %s", what, event.src_path)
        if ndx.can_ignore(event.src_path):
            return

        if event.is_directory:
            file_path = ndx.relpath(event.src_path)
            self.broadcast_created_directory(file_path)
        else:
            with open(event.src_path, 'r') as f:
                file_path = ndx.relpath(event.src_path)
                filehash, blob = ndx.add_file(ndx.relpath(file_path))
                file = ndx.get_file_meta(file_path)
                if file:
                    data = {
                        'path': file.file_path,
                        'hash': file.hash,
                        'revision': file.revision,
                        'file_type': file.file_type,
                        'link_src': file.link_src,
                        'modified_at': file.modified_at
                    }
                else:
                    data = {}
                from index import normalize_file_path
                self.broadcast_created_file(normalize_file_path(file_path), data, blob)

    def on_deleted(self, event):
        if '.kd-cache' in event.src_path:
            return
        what = 'directory' if event.is_directory else 'file'
        logger.info("Deleted %s: %s", what, event.src_path)


    def on_modified(self, event):
        what = 'directory' if event.is_directory else 'file'

        if event.src_path == ndx.root_path or ndx.can_ignore(event.src_path):
            return

        logger.info("> -  Modified %s: %s", what, event.src_path)

        if event.is_directory:
            # TODO:
            # when a directory is modified,
            # we check the tree under it,
            # because somehow on macs, pycharm doesnt trigger
            # file changes
            pass
        else:
            with open(event.src_path, 'r') as f:
                content = f.read()
                file_path = ndx.relpath(event.src_path)
                patches = ndx.update_file(file_path, content)
                if not patches:
                    print "no patches... nothing changed ??"
                if patches:
                    # TODO: we need to send old hash too
                    file = ndx.get_file_meta(file_path)
                    data = {
                        'path': file.file_path,
                        'hash': file.hash,
                        'revision': file.revision,
                        'file_type': file.file_type,
                        'link_src': file.link_src,
                        'modified_at': file.modified_at
                    }
                    self.broadcast_update_file(file_path, data, pickle.dumps(patches))

    def broadcast_created_directory(self, file_path):
        # TODO: send permissions
        print "broadcasting directory created - ", file_path
        for client in clients:
            client.send_cmd('directory_created', file_path)

    def broadcast_created_file(self, file_path, data, blob):
        print "broadcast created file."
        for client in clients:
            client.send_cmd('file_created', file_path, data, blob)

    def broadcast_update_file(self, file_path, data, patches):
        print "broadcast update file."
        for client in clients:
            client.send_cmd('file_modified', file_path, data, patches)

# this is our global registry of
# connected clients, we use only one server process
clients = set()

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('new connection')
        self.client_name = ''
        clients.add(self)
        self.actions = Actions(ndx, send_cmd_fn=self.send_cmd, remote=self)

    def fetch_file(self, file_path, hash):
        self.send_cmd('send_file', file_path, hash)

    def send_cmd(self, cmd, *args, **kwargs):
        """
        sends command to the client side.
        """
        n = dict(cmd=cmd, args=args)
        if kwargs:
            n.update(kwargs)
        self.write_message(pickle.dumps(n))

    def parse_message(self, message):
        """
        this is our dispatcher
        """
        o = pickle.loads(str(message))
        fn = getattr(self.actions, 'cmd_%s' % o['cmd'], None)
        if not fn:
            logger.debug("[%s] command not found - %s ", self.client_name, o['cmd'], )
            return
        if fn:
            logger.debug("[%s] calling - %s %s", self.client_name, o['cmd'], o['args'])
            args = o['args']
            del o['args']
            del o['cmd']
            try:
                if o:
                    fn(*args, **o)
                else:
                    fn(*args)
            except Exception as e:
                logger.exception("exception while running command %s ", fn)

    def on_message(self, message):
        try:
            self.parse_message(message)
        except Exception as e:
            logger.exception("exception while parsing message")
            raise

    def on_close(self):
        print('connection closed')
        clients.remove(self)

application = tornado.web.Application([
    (r'/', WSHandler),
])

def periodic_callback():
    listeners = [indexlistener, serverlistener]
    try:
        job = queue.get(False)
        for listener in listeners:
            event = job[1]
            fn = getattr(listener, 'on_%s' % job[0])
            fn(event)
    except Empty as e:
        pass

def run_server(path=None, log_file_name='server.log'):
    global indexlistener, serverlistener, queue, ndx

    port = 8888

    def sigtermhandler(*args):
        logger.debug("sig term caught....")
        logger.debug("stopping observer")
        observer.stop()
        observer.join()
        logger.debug("stopping loop")
        tornado.ioloop.IOLoop.instance().stop()

    signal.signal(signal.SIGTERM, sigtermhandler)

    if not path:
        path = os.path.abspath(sys.argv[1])
    else:
        path = os.path.abspath(path)

    queue = Queue()
    observer  = watcher.create_watcher_process(path, queue)
    server = {}

    ndx = index.SyncIndex(os.path.abspath(path))
    indexlistener = watcher.IndexListener(ndx, inserver=True)
    serverlistener = ServerEventListener(server)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    logger.info("starting to listen on %s", port)

    io_loop = tornado.ioloop.IOLoop.instance()
    pc = tornado.ioloop.PeriodicCallback(periodic_callback, 100)
    pc.start()
    io_loop.start()


if __name__ == "__main__":
    run_server()