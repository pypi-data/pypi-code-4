from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logging
import sys
import os
import time
from index import SyncIndex
import multiprocessing
import cPickle as pickle
from index import normalize_file_path

class IndexListener(object):
    def __init__(self, syncindex):
        self.syncindex = syncindex
        self.remoteindex = None

    def set_remote_index(self, remoteindex):
        self.remoteindex = remoteindex

    def on_moved(self, event):
        if self.syncindex.can_ignore(event.src_path):
            return
        what = 'directory' if event.is_directory else 'file'
        logging.info("Moved %s: from %s to %s", what, event.src_path,
                 event.dest_path)

    def on_created(self, event):
        if self.syncindex.can_ignore(event.src_path):
            return
        what = 'directory' if event.is_directory else 'file'
        logging.info("Created %s: %s", what, event.src_path)
        # TODO: cleanup with on_modified, they are almost the same...
        print "time:", time.time()
        file_path = self.syncindex.relpath(event.src_path)
        if matches_dir(event.src_path, [os.path.join(self.syncindex.root_path, i) for i in self.syncindex.exclude_paths]):
            print "ignoring file", event.src_path
            return
        if event.is_directory:
            if self.remoteindex:
                self.remoteindex.created_local_directory(normalize_file_path(file_path))
        else:
            with open(event.src_path, 'r') as f:
                filehash, blob = self.syncindex.add_file(self.syncindex.relpath(file_path))
                if self.remoteindex:
                    file = self.syncindex.get_file_meta(file_path)
                    if not file:
                        raise Exception("couldnt find file on db - %s" % file_path)

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
                    self.remoteindex.created_local_file(normalize_file_path(file_path), data, blob)

    def on_deleted(self, event):
        if self.syncindex.can_ignore(event.src_path):
            return
        if matches_dir(event.src_path, [os.path.join(self.syncindex.root_path, i) for i in self.syncindex.exclude_paths]):
            logging.debug("ignoring file %s", event.src_path)
            return
        what = 'd' if event.is_directory else 'f'
        logging.info("Deleted %s: %s", what, event.src_path)

        from index import normalize_file_path
        file_path = self.syncindex.relpath(event.src_path)
        self.syncindex.remove_file(file_path, what)
        if self.remoteindex:
            self.remoteindex.removed_local_file(normalize_file_path(file_path), what)

    def on_modified(self, event):
        what = 'directory' if event.is_directory else 'file'
        print "time:", time.time()
        logging.info("Modified %s: %s", what, event.src_path)
        if self.syncindex.can_ignore(event.src_path):
            logging.debug("ignored - %s", event.src_path)
            return
        if event.is_directory:
            pass
        else:
            if matches_dir(event.src_path, [os.path.join(self.syncindex.root_path, i) for i in self.syncindex.exclude_paths]):
                logging.debug("ignoring file %s", event.src_path)
                return
            with open(event.src_path, 'r') as f:
                content = f.read()
                file_path = self.syncindex.relpath(event.src_path)
                patches = self.syncindex.update_file(file_path, content)
                if patches and self.remoteindex:
                    # TODO: we need to send old hash too
                    file = self.syncindex.get_file_meta(file_path)
                    data = {
                        'path': file['file_path'],
                        'hash': file['hash'],
                        'revision': file['revision'],
                        'file_type': file['file_type'],
                        'link_src': file['link_src'],
                        'modified_at': file['modified_at']
                    }
                    from index import normalize_file_path
                    self.remoteindex.updated_local_file(normalize_file_path(file_path), data, pickle.dumps(patches))

def matches_dir(path, pats):
    """
    checks if path is a subdir or same directory of one of pats
    :param path: 
    :param pats:

    >>> matches_dir("/foo/bar", ["/foo/bar"])
    True
    >>> matches_dir("/foo/bar/baz", ["/foo/bar"])
    True
    >>> matches_dir("/foo/bar/baz/boo", ["/foo/bar"])
    True
    >>> matches_dir("/foo/bar/baz", ["/foo/ba"])
    False
    >>> matches_dir("foo/bar/baz", ["foo/ba"])
    False

    """
    for pat in pats:
        if pat == path:
            return True
        if not pat.endswith(os.sep):
            pat += os.sep
        if path.startswith(pat):
            return True
    return False


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

def watcher(queue, path):
    event_handler = MultiProcessEventHandler(queue)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def create_watcher_process(path):
    jobq = multiprocessing.Queue()
    p = multiprocessing.Process(target=watcher, args=(jobq, path))
    p.start()
    return (p, jobq)

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

