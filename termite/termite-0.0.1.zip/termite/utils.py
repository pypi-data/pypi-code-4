import os
import shutil
import logging
from functools import partial, wraps
from time import sleep

import sarge
import tornado
from glob2 import iglob

from termite.server import SSEHandler


def _as_list(obj):
    """Returns an object as a list.

    Ensure that the object type is tuple, set or list, if not put the element
    in a list and return this new list.

    Args:
        obj: Object you want to check.
    Returns:
        An iterable with type tuple, set or list.
    """
    if type(obj) in (tuple, set, list):
        return obj
    else:
        return [obj]


def copy_rec(source, dest):
    """Copy files between diferent directories.

    Copy one or more files to an existing directory. This function is
    recursive, if the source is a directory, all its subdirectories are created
    in the destination. Existing files in destination are overwrited without
    any warning.

    Args:
        source (str): File or directory name.
        dest (str): Directory name.

    Raises:
        FileNotFoundError: Destination directory doesn't exist.
    """

    if os.path.isdir(source):
        for child in os.listdir(source):
            new_dest = os.path.join(dest, child)
            os.makedirs(new_dest, exist_ok=True)
            copy_rec(os.path.join(source, child), new_dest)

    elif os.path.isfile(source):
        logging.info(' Copy "{}" to "{}"'.format(source, dest))
        shutil.copy(source, dest)

    else:
        logging.info(' Ignoring "{}"'.format(source))


def shell_creator(command, watch=None, cwd=None):
    def shell(command_, cwd_):
        for comm in _as_list(command_):
            logging.info('-----')
            logging.info(' Running: ' + comm)
            sarge.run(comm, cwd=cwd_)

    function = partial(shell, command, cwd)
    if watch:
        Watcher(watch, function)
    function()


def cp_creator(source, dest, watch=None):
    def cp(sources, dest):
        """Copy a file or a list of files.

        Copy one or more files. Also is possible copy directories.  There is
        one different between this two sources, `some/folder` and
        `/some/folder/*`. In the first case the folder is copied to the
        destination, in the second case the files inside the directory are
        copied, but not the directory itself.
        """
        logging.info('-----')

        for source in _as_list(sources):
            for path in iglob(source):
                copy_rec(path, dest)

    if (not os.path.exists(dest)) and (
            type(source) is list or dest.endswith('/')):
        os.makedirs(dest)

    function = partial(cp, source, dest)
    if watch:
        Watcher(source, function)
    function()


# TODO move inside create_task
def set_server(path):
    Watcher.server_path = path


def create_task(task, args):
    if task == 'shell':
        shell_creator(**args)
    elif task == 'cp':
        cp_creator(**args)
    elif task == 'server':
        set_server(**args)


# TODO Not used right now
def retry(func=None, *, tries=3):

    if func is None:
        return partial(retry, tries=tries)

    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(tries):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError:
                if attempt + 1 == tries:
                    raise
                sleep(0.1)

    return wrapper


class Watcher:

    watchers = []
    server_path = None

    def __init__(self, path, function):
        self.files = Files(path)
        self.function = function

        Watcher.watchers.append(self)

    #@retry
    #def check(self):
    #    '''Return True if there are changes'''
    #    # Returns FileNotFoundError sometimes, because the check is done when
    #    # other process, mainly the editor, is writing the file.
    #    mtime = os.path.getmtime(self.path)
    #    if mtime != self.mtime:
    #        self.mtime = mtime
    #        self.function()
    #        return True

    #    return False

    def check(self):

        if self.files.changes():
            self.function()
            return True

        return False

    @classmethod
    def check_all(cls):
        changes = False
        for watch in cls.watchers:
            if watch.check():
                changes = True

        if changes and cls.is_server():
            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.add_callback(lambda x: x.send_reload_events(), SSEHandler)

    @classmethod
    def is_empty(cls):
        if len(cls.watchers) == 0:
            return True
        else:
            return False

    @classmethod
    def is_server(cls):
        if cls.server_path is None:
            return False
        else:
            return True


class Files:
    '''/some/dir/ is the same as /some/dir/** '''

    def __init__(self, original_path):

        self.origins = _as_list(original_path)
        self.paths = self._get_mtimes(self.origins)

    def get_changes(self):
        new = set()
        modified = set()
        not_modified = set()

        for path, mtime in self._get_mtimes(self.origins).items():
            try:
                if self.paths[path] != mtime:
                    modified.add(path)
                else:
                    not_modified.add(path)
            except KeyError:
                new.add(path)
            self.paths[path] = mtime

        deleted = self.paths.keys() - new - modified - not_modified
        for item in deleted:
            del self.paths[item]

        return modified, new, deleted

    def changes(self):

        changes = 0

        for item in self.get_changes():
            changes += len(item)

        if changes == 0:
            return False
        else:
            return True

    @staticmethod
    def _get_mtimes(paths):

        files = {}

        for path in paths:

            if '*' not in path and not os.path.exists(path):
                logging.error("WARNING, file not found: '{}'".format(path))

            if os.path.isdir(path):
                path = '{}/{}'.format(path.rstrip('/'), '**')

            for file_path in iglob(path):
                if os.path.isfile(file_path):
                    files[file_path] = os.path.getmtime(file_path)

        return files
