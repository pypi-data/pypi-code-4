from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logging
import sys
import os
import time
from index import SyncIndex
import cPickle as pickle
from index import normalize_file_path

class IndexListener(object):
    def __init__(self, syncindex, inserver=False):
        self.syncindex = syncindex
        self.remoteindex = None
        self.inserver=inserver

    def set_remote_index(self, remoteindex):
        self.remoteindex = remoteindex

    def on_moved(self, event):
        if self.syncindex.can_ignore(event.src_path):
            return
        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                 event.dest_path)

    def on_created(self, event):
        src_path = event.src_path
        if event.is_directory:
            src_path = event.src_path + os.path.sep

        if self.syncindex.can_ignore(src_path):
            return
        what = 'directory' if event.is_directory else 'file'
        file_path = self.syncindex.relpath(src_path)
        logging.info("Created %s: %s", what, src_path)

        # TODO: cleanup with on_modified, they are almost the same...
        if event.is_directory:
            if self.remoteindex:
                self.remoteindex.created_local_directory(normalize_file_path(file_path))
        else:
            with open(src_path, 'r') as f:
                filehash, blob = self.syncindex.add_file(self.syncindex.relpath(file_path))
                if self.remoteindex:
                    file = self.syncindex.get_file_meta(file_path)
                    if not file:
                        raise Exception("couldnt find file on db - %s" % file_path)

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
                    self.remoteindex.created_local_file(normalize_file_path(file_path), data, blob)

    def on_deleted(self, event):
        if self.syncindex.can_ignore(event.src_path):
            print "ignorable by can_ignore"
            return

        what = 'd' if event.is_directory else 'f'
        logging.info("Deleted %s: %s", what, event.src_path)

        from index import normalize_file_path
        file_path = self.syncindex.relpath(event.src_path)
        self.syncindex.remove_file(file_path, what)
        if self.remoteindex:
            self.remoteindex.removed_local_file(normalize_file_path(file_path), what)

    def on_modified(self, event):
        if self.inserver:
            return

        what = 'directory' if event.is_directory else 'file'

        if self.syncindex.can_ignore(event.src_path):
            return

        logging.info("Modified %s: %s", what, event.src_path)

        if event.is_directory:
            pass
        else:
            with open(event.src_path, 'r') as f:
                content = f.read()
                file_path = self.syncindex.relpath(event.src_path)
                patches = self.syncindex.update_file(file_path, content)
                if patches and self.remoteindex:
                    # TODO: we need to send old hash too
                    file = self.syncindex.get_file_meta(file_path)
                    data = {
                        'path': file.file_path,
                        'hash': file.hash,
                        'revision': file.revision,
                        'file_type': file.file_type,
                        'link_src': file.link_src,
                        'modified_at': file.modified_at
                    }
                    from index import normalize_file_path
                    self.remoteindex.updated_local_file(normalize_file_path(file_path), data, pickle.dumps(patches))

class MultiProcessEventHandler(FileSystemEventHandler):
    """
    when something happens, this pushes to queue, because threads are evil
    they say
    """
    def __init__(self, queue):
        self.queue = queue

    def on_moved(self, event):
        super(MultiProcessEventHandler, self).on_moved(event)
        self.queue.put("moved", event)

    def on_created(self, event):
        super(MultiProcessEventHandler, self).on_created(event)
        self.queue.put(("created", event))

    def on_deleted(self, event):
        super(MultiProcessEventHandler, self).on_deleted(event)
        self.queue.put(("deleted", event))

    def on_modified(self, event):
        super(MultiProcessEventHandler, self).on_modified(event)
        self.queue.put(("modified", event))

#def watcher_(queue, message_queue, path):
#    event_handler = MultiProcessEventHandler(queue)
#    observer = Observer()
#    observer.schedule(event_handler, path, recursive=True)
#    observer.start()
#    try:
#        print "ffff"
#        message_queue.get()
#        print "heeeeee"
#    finally:
#        print "stopping observer...."
#        observer.stop()
#        print "done...."
#    observer.join()
#    print "Returning...."

def create_watcher_process(path, jobq):
    print ">>>> create_watcher_process"
    #jobq = multiprocessing.Queue()
    # we use this to communicate with main process,
    # so we can stop the observer thread easily
    #messageq = multiprocessing.Queue()
    event_handler = MultiProcessEventHandler(jobq)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer

    #try:
    #    message_queue.get()
    #finally:
    #    observer.stop()
    #observer.join()

    #return observer, jobq

    #p = multiprocessing.Process(target=watcher_, args=(jobq, messageq, path))
    #p.start()
    #return (p, jobq, messageq)

if __name__ == '__main__':
    path = sys.argv[1]
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    index = SyncIndex(os.path.abspath(path))
    listener = IndexListener(index)

    process, queue = create_watcher_process(path)
    while True:
        job = queue.get()
        fn = getattr(listener, 'on_%s' % job[0])
        fn(job[1])

