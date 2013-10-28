import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import watcher
import logging
import index
import os
import sys
import time
import matcher
import diff_match_patch
from Queue import Empty
import cPickle as pickle


class ServerEventListener(object):
    def __init__(self, server):
        self.server = server

    def on_moved(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                 event.dest_path)

    def on_created(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)
        if ndx.can_ignore(event.src_path):
            return
        print "time:", time.time()

        if watcher.matches_dir(event.src_path, [os.path.join(ndx.root_path, i) for i in ndx.exclude_paths]):
            print "ignoring file", event.src_path
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
                        'path': file['file_path'],
                        'hash': file['hash'],
                        'revision': file['revision'],
                        'file_type': file['file_type'],
                        'link_src': file['link_src'],
                        'modified_at': file['modified_at']
                    }
                else:
                    data = {}
                from index import normalize_file_path
                self.broadcast_created_file(normalize_file_path(file_path), data, blob)

    def on_deleted(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        what = 'directory' if event.is_directory else 'file'
        logging.info("Modified %s: %s", what, event.src_path)
        print "time:", time.time()

        if ndx.can_ignore(event.src_path):
            return

        if event.is_directory:
            # TODO:
            # when a directory is modified,
            # we check the tree under it,
            # because somehow on macs, pycharm doesnt trigger
            # file changes
            if watcher.matches_dir(event.src_path, [os.path.join(ndx.root_path, i) for i in ndx.exclude_paths]):
                print "ignoring directory", event.src_path
                return

        else:
            if watcher.matches_dir(event.src_path, [os.path.join(ndx.root_path, i) for i in ndx.exclude_paths]):
                print "ignoring file", event.src_path
                return
            with open(event.src_path, 'r') as f:
                content = f.read()
                file_path = ndx.relpath(event.src_path)
                patches = ndx.update_file(file_path, content)
                if patches:
                    # TODO: we need to send old hash too
                    file = ndx.get_file_meta(file_path)
                    data = {
                        'path': file['file_path'],
                        'hash': file['hash'],
                        'revision': file['revision'],
                        'file_type': file['file_type'],
                        'link_src': file['link_src'],
                        'modified_at': file['modified_at']
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

    def cmd_exit(self):
        sys.exit(0)

    def cmd_removed_file(self, file_path, file_type):
        fpath = os.path.join(ndx.root_path, file_path)
        if os.path.exists(fpath):
            os.remove(fpath)

    def cmd_directory_created(self, file_path):
        meta = ndx.get_file_meta(file_path)
        if meta:
            # check if we have
            pass
        fpath = os.path.join(ndx.root_path, file_path)
        try:
            os.makedirs(fpath)
        except Exception as e:
            print "Exception while creating directories [", e, "]"


    def cmd_created_local_file(self, file_path, data, blob):
        file = ndx.get_file_meta(file_path)
        if not file:
            # everything is cool if we stll dont have the file
            # just save the file, watcher will take care of the rest
            fpath = os.path.join(ndx.root_path, file_path)
            with open(fpath, 'w') as f:
                f.write(blob)
        else:
            if file['hash'] == data['hash']:
                logging.debug("same hash, ignoring.")
                return

            # houston we might have a problem...
            # we have the file but some client thinks
            # it wasnt in the index
            logging.error("client says new file but we have the file - [%s] - [%s]", file_path, data['hash'])

    def cmd_updated_local_file(self, file_path, data, pickled_patch):
        file = ndx.get_file_meta(file_path)
        if not file:
            # TODO: we might not have the file yet,
            # or not indexed yet... etc.
            # then we should ask the client to send us the
            # whole thing..
            pass
        else:

            if file['hash'] == data['hash']:
                logging.debug("same hash, ignoring.")
                return

            # we apply the patches to our local file.
            # file watcher should take care of the rest - reindexing etc..
            patches = pickle.loads(str(pickled_patch))
            fpath = os.path.join(ndx.root_path, file_path)
            with open(fpath, 'r') as f:
                data = f.read()

            with open(fpath, 'w') as f:
                dmp = diff_match_patch.diff_match_patch()
                dmp.Diff_Timeout = 0
                newdata, results = dmp.patch_apply(patches, data)
                f.write(newdata)

    def cmd_fetch_file(self, file_path, hash):
        file = ndx.get_file_meta(file_path)
        blob = ndx.get_blob(file['hash'])
        assert file['hash'] == hash
        ret = {
                'path': file['file_path'],
                'hash': file['hash'],
                'revision': file['revision'],
                'file_type': file['file_type'],
                'link_src': file['link_src'],
                'modified_at': file['modified_at'],
                'blob': blob
        }
        self.send_cmd('fetch_file_reply', file_path, ret)

    def cmd_send_file_reply(self, file_path, data):
        logging.debug('saving file %s ', file_path)
        with open(os.path.join(ndx.root_path, file_path), 'w') as f:
            f.write(data['blob'])

    def fetch_file(self, file_path, hash):
        self.send_cmd('send_file', file_path, hash)

    def cmd_sync_files(self, files):
        print "files", files
        ndx.sync_files(files, self)

    def cmd_get_file_list(self):
        files = ndx.files()
        ret = []
        for file in files:
            ret.append({
                'path': file['file_path'],
                'hash': file['hash'],
                'revision': file['revision'],
                'file_type': file['file_type'],
                'link_src': file['link_src'],
                'modified_at': file['modified_at']
            })
        self.send_cmd('file_list',  ret)

    def send_cmd(self, cmd, *args, **kwargs):
        n = dict(cmd=cmd, args=args)
        if kwargs:
            n.update(kwargs)
        self.write_message(pickle.dumps(n))

    def cmd_set_name(self, name):
        self.client_name = name

    def parse_message(self, message):
        o = pickle.loads(str(message))
        fn = getattr(self, 'cmd_%s' % o['cmd'], None)
        if not fn:
            logging.debug("[%s] command not found - %s ", self.client_name, o['cmd'], )
            return
        if fn:
            logging.debug("[%s] calling - %s ", self.client_name, o['cmd'], )
            args = o['args']
            del o['args']
            del o['cmd']
            try:
                if o:
                    fn(*args, **o)
                else:
                    fn(*args)
            except Exception as e:
                print ">>> exception - ", e

    def on_message(self, message):
        print "received message", message
        try:
            self.parse_message(message)
        except Exception as e:
            print e
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

def run_server(path=None):
    global indexlistener, serverlistener, process, queue, ndx
    if not path:
        path = os.path.abspath(sys.argv[1])
    else:
        path = os.path.abspath(path)
    process, queue = watcher.create_watcher_process(path)
    server = {}

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    ndx = index.SyncIndex(os.path.abspath(path))
    indexlistener = watcher.IndexListener(ndx)
    serverlistener = ServerEventListener(server)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    io_loop = tornado.ioloop.IOLoop.instance()
    pc = tornado.ioloop.PeriodicCallback(periodic_callback, 100)
    pc.start()
    io_loop.start()

if __name__ == "__main__":
    run_server()