import tornado
from tornado.websocket import websocket_connect
import errno
import watcher
import index
import sys
import os
import signal
from Queue import Empty
import cPickle as pickle
import socket
import transporter.diff_match_patch as diff_match_patch
from Queue import Queue
from transporter.actions import Actions
from datetime import timedelta

from transporter.log import get_logger
logger = get_logger("client")

PING_TIMEOUT = 15

class WebSocketClient():
    conn = None
    keepalive = None
  
    def __init__(self, uri, observer):
        self.actions = Actions(syncindex, send_cmd_fn=self.send_cmd)
        self.observer = observer
        self.uri = uri
        self.doconn()
  
    def doconn(self):
        w = websocket_connect(self.uri)
        w.add_done_callback(self.wsconnection_cb)

    def send_hello(self):
        self.send_cmd('set_name', socket.gethostname())

    def send_get_file_list(self):
        self.send_cmd('get_file_list')

    def dokeepalive(self):
        stream = self.conn.protocol.stream
        if not stream.closed():
            self.keepalive = stream.io_loop.add_timeout(timedelta(seconds=PING_TIMEOUT),
                                                        self.dokeepalive)
            self.conn.protocol.write_ping("")
        else:
            self.keepalive = None # should never happen

    def send_cmd(self, cmd, *args, **kwargs):
        logger.debug("sending command to server - %s", cmd)
        n = dict(cmd=cmd, args=args)
        if kwargs:
            n.update(kwargs)
        self.conn.write_message(pickle.dumps(n))

    def wsconnection_cb(self, conn):
        self.conn = conn.result()
        self.conn.on_message = self.message
        self.keepalive = tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=PING_TIMEOUT),
                                                                      self.dokeepalive)
        self.send_hello()
        self.send_get_file_list()

    def on_file_list(self, files):
        syncindex.sync_files(files, self)
        # TODO: make sure first remote sync is over...
        self.sync_our_files()

    def message(self, msg):
        try:
            self._message(msg)
        except Exception as e:
            logger.exception("Exception while unpickling message")

    def _message(self, message):
        if not message:
            return
        o = pickle.loads(str(message))
        fn = getattr(self, 'on_%s' % o['cmd'], None)
        if not fn:
            fn = getattr(self.actions, 'cmd_%s' % o['cmd'], None)

        if not fn:
            logger.debug("[%s] command not found - %s ", "[server]", o['cmd'], )
            raise Exception("command not found")

        if fn:
            logger.debug("[%s] calling - %s ", "[server]", o['cmd'], )
            args = o['args']
            del o['args']
            del o['cmd']
            try:
                if o:
                    fn(*args, **o)
                else:
                    fn(*args)
            except Exception as e:
                logger.exception("Exception handling message - %s " % o)


    def close(self):
        print "connection closed, quitting"
        self.observer.stop()
        tornado.ioloop.IOLoop.instance().stop()

    def removed_local_file(self, file_path, file_type):
        self.send_cmd('removed_file', file_path, file_type)

    def fetch_file(self, file_path, hash):
        logger.debug("fetch from remote %s", file_path)
        self.send_cmd('fetch_file', file_path, hash)

    def created_local_directory(self, file_path):
        # TODO: send perms
        logger.debug("sending directory created %s", file_path)
        self.send_cmd('directory_created', file_path)

    def created_local_file(self, file_path, data, blob):
        self.send_cmd('file_created', file_path, data, blob)

    def updated_local_file(self, file_path, data, patch):
        logger.debug("updated local file")
        self.send_cmd('file_modified', file_path, data, patch)

    def send_our_file(self, file_path, data, blob):
        logger.debug("send our file")

    def sync_our_files(self):
        logger.debug("sync our files...")
        files = syncindex.files()
        ret = []
        for file in files:
            ret.append({
                'path': file.file_path,
                'hash': file.hash,
                'revision': file.revision,
                'file_type': file.file_type,
                'link_src': file.link_src,
                'modified_at': file.modified_at
            })
        self.send_cmd('sync_files', ret)

def periodic_callback():
    listeners = [indexlistener]
    try:
        while True:
            job = queue.get(False)
            for listener in listeners:
                event = job[1]
                fn = getattr(listener, 'on_%s' % job[0])
                fn(event)
    except Empty as e:
        pass

def run_client(path=None, uri=None, child_conn=None):
    # TODO: yeah...
    global queue, ndx, indexlistener, syncindex, \
           message_que

    def app_connection_check():
        c = app_conn.poll(0.100)
        if c:
            data = app_conn.recv()
            print ">>> received from app >>>", c, data
            observer.stop()
            observer.join()
            tornado.ioloop.IOLoop.instance().stop()

    def sigtermhandler(*args):
        print "on sig term handler...."
        observer.stop()
        observer.join()
        tornado.ioloop.IOLoop.instance().stop()

    signal.signal(signal.SIGTERM, sigtermhandler)

    if not path:
        path = sys.argv[1]

    app_conn = None
    if child_conn:
        child_conn.poll(0.1)
        app_conn = child_conn

    if not uri:
        ws_uri = sys.argv[2]
    else:
        ws_uri = uri
    ws_uri = ws_uri.replace('http://', 'ws://')
    logger.info("connecting to %s", ws_uri)

    queue = Queue()
    observer = watcher.create_watcher_process(path, queue)
    syncindex = index.SyncIndex(os.path.abspath(path))
    indexlistener = watcher.IndexListener(syncindex)

    try:
        io_loop = tornado.ioloop.IOLoop.instance()
        wsclient = WebSocketClient(ws_uri, observer)
        indexlistener.set_remote_index(wsclient)
        io_loop = tornado.ioloop.IOLoop.instance()
        periodic_cb = tornado.ioloop.PeriodicCallback(periodic_callback, 10)
        periodic_cb.start()

        if app_conn:
            app_conn_checker = tornado.ioloop.PeriodicCallback(app_connection_check, 100)
            app_conn_checker.start()

        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        io_loop.stop()

    sigtermhandler()


if __name__ == '__main__':
    run_client()