import tornado
from tornado.websocket import websocket_connect
from datetime import timedelta
import watcher
import logging
import index
import sys
import os
import signal
from Queue import Empty
import cPickle as pickle
import socket
import time
import diff_match_patch

#echo_uri = 'ws://echo.websocket.org'
#echo_uri = 'ws://ws.blockchain.info/inv'
#echo_uri = 'ws://localhost:8888/'
#echo_uri = 'ws://ybrs2.kd.io:8888/'

PING_TIMEOUT = 15

class WebSocketClient():
    conn = None
    keepalive = None
  
    def __init__(self, uri):
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
            self.keepalive = stream.io_loop.add_timeout(timedelta(seconds=PING_TIMEOUT), self.dokeepalive)
            self.conn.protocol.write_ping("")
        else:
            self.keepalive = None # should never happen

    def send_cmd(self, cmd, *args, **kwargs):
        logging.debug("sending command to server - %s", cmd)
        n = dict(cmd=cmd, args=args)
        if kwargs:
            n.update(kwargs)
        self.conn.write_message(pickle.dumps(n))

    def wsconnection_cb(self, conn):
        self.conn = conn.result()
        self.conn.on_message = self.message
        self.keepalive = tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=PING_TIMEOUT), self.dokeepalive)
        self.send_hello()
        self.send_get_file_list()

    def on_file_list(self, files):
        syncindex.sync_files(files, self)
        # TODO: make sure first remote sync is over...
        self.sync_our_files()

    def on_directory_created(self, file_path):
        meta = syncindex.get_file_meta(file_path)
        if meta:
            pass
        fpath = os.path.join(syncindex.root_path, file_path)
        try:
            os.makedirs(fpath)
        except Exception as e:
            print "Exception while creating directories [", e, "]"

    def on_file_created(self, file_path, data, blob):
        file = syncindex.get_file_meta(file_path)
        if not file:
            # everything is cool if we stll dont have the file
            # just save the file, watcher will take care of the rest
            fpath = os.path.join(syncindex.root_path, file_path)
            with open(fpath, 'w') as f:
                f.write(blob)
        else:
            if file['hash'] == data['hash']:
                logging.debug("same hash, ignoring.")
                return

            # houston we might have a problem...
            # we have the file but some client thinks
            # it wasnt in the index
            logging.error("server says new file but we have the file - [%s] - [%s]", file_path, data['hash'])


    def on_file_modified(self, file_path, data, patches):
        file = syncindex.get_file_meta(file_path)

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
            patches = pickle.loads(str(patches))
            fpath = os.path.join(syncindex.root_path, file_path)
            with open(fpath, 'r') as f:
                data = f.read()

            with open(fpath, 'w') as f:
                dmp = diff_match_patch.diff_match_patch()
                dmp.Diff_Timeout = 0
                newdata, results = dmp.patch_apply(patches, data)
                f.write(newdata)


    def message(self, msg):
        try:
            self._message(msg)
        except Exception as e:
            print "exception while handling message: ", msg
            import traceback
            traceback.print_exc()

    def _message(self, message):
        if not message:
            return
        o = pickle.loads(str(message))
        fn = getattr(self, 'on_%s' % o['cmd'], None)
        if not fn:
            logging.debug("[%s] command not found - %s ", "[server]", o['cmd'], )

        if fn:
            logging.debug("[%s] calling - %s ", "[server]", o['cmd'], )
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

    def close(self):
        print "connection closed, quitting"
        tornado.ioloop.IOLoop.instance().stop()
        process.terminate()

    def on_fetch_file_reply(self, file_path, data):
        logging.debug('saving file %s ', file_path)
        meta = syncindex.get_file_meta(file_path)
        if not meta:
            with open(os.path.join(syncindex.root_path, file_path), 'w') as f:
                f.write(data['blob'])
        else:
            # do a merge operation...
            patches = syncindex.update_file(file_path, data['blob'])
            fpath = os.path.join(syncindex.root_path, file_path)
            with open(fpath, 'r') as f:
                data = f.read()

            with open(fpath, 'w') as f:
                dmp = diff_match_patch.diff_match_patch()
                dmp.Diff_Timeout = 0
                newdata, results = dmp.patch_apply(patches, data)
                f.write(newdata)

    def on_send_file(self, file_path, hash):
        file = syncindex.get_file_meta(file_path)
        blob = syncindex.get_blob(file['hash'])
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
        self.send_cmd('send_file_reply', file_path, ret)

    def removed_local_file(self, file_path, file_type):
        self.send_cmd('removed_file', file_path, file_type)

    def fetch_file(self, file_path, hash):
        logging.debug("fetch from remote %s", file_path)
        self.send_cmd('fetch_file', file_path, hash)

    def created_local_directory(self, file_path):
        # TODO: send perms
        logging.debug("sending directory created %s", file_path)
        self.send_cmd('directory_created', file_path)

    def created_local_file(self, file_path, data, blob):
        self.send_cmd('created_local_file', file_path, data, blob)

    def updated_local_file(self, file_path, data, patch):
        logging.debug("updated local file")
        self.send_cmd('updated_local_file', file_path, data, patch)

    def send_our_file(self, file_path, data, blob):
        logging.debug("send our file")

    def sync_our_files(self):
        logging.debug("sync our files...")
        files = syncindex.files()
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

def run_client(path=None, uri=None):
    global process, queue, ndx, indexlistener, syncindex, ws_uri
    if not path:
        path = sys.argv[1]

    if not uri:
        ws_uri = sys.argv[2]
    else:
        ws_uri = uri
    ws_uri = ws_uri.replace('http://', 'ws://')
    print "connect to:", ws_uri

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    process, queue = watcher.create_watcher_process(path)
    syncindex = index.SyncIndex(os.path.abspath(path))
    indexlistener = watcher.IndexListener(syncindex)

    try:
        io_loop = tornado.ioloop.IOLoop.instance()
        wsclient = WebSocketClient(ws_uri)
        indexlistener.set_remote_index(wsclient)
        io_loop = tornado.ioloop.IOLoop.instance()
        pc = tornado.ioloop.PeriodicCallback(periodic_callback, 10)
        pc.start()
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        io_loop.stop()


if __name__ == '__main__':
    run_client()