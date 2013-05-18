import os
import time
import errno
import psutil
import subprocess
import json
import sys
from v12 import env


class FileLockException(Exception):
    pass


class FileLock(object):
    """ A file locking mechanism that has context-manager support so 
        you can use it in a with statement.
    """

    lock_manifest = set()

    def __init__(self, file_name, timeout=10, delay=.1):
        """ Prepare the file locker. Specify the file to lock and optionally
            the timeout and the delay between each attempt to lock.
        """
        self.is_locked = False
        self.filepath = os.path.abspath(file_name)
        self.lock_filepath = "%s.lock" % self.filepath
        self.timeout = timeout
        self.delay = delay

    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws 
            an exception.
        """
        start_time = time.time()
        while True:
            try:
                with os.fdopen(os.open(self.lock_filepath, os.O_CREAT | os.O_EXCL | os.O_RDWR), "w") as lock_file:
                    lock_file.write(str(os.getpid()))
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

                with open(self.lock_filepath) as lock_file:
                    lock_file_pid = lock_file.read()

                if not lock_file_pid or not psutil.pid_exists(int(lock_file_pid)):
                    os.remove(self.lock_filepath)
                    continue

                if (time.time() - start_time) >= self.timeout:
                    raise FileLockException("Timeout occured.")
                time.sleep(self.delay)

        self.is_locked = True
        FileLock.lock_manifest.add(self.filepath)

    def release(self):
        """ Get rid of the lock by deleting the lockfile. 
            When working in a `with` statement, this gets automatically 
            called at the end.
        """
        if self.is_locked:
            os.remove(self.lock_filepath)
            self.is_locked = False
            FileLock.lock_manifest.remove(self.filepath)

    def __enter__(self):
        """ Activated when used in the with statement. 
            Should automatically acquire a lock to be used in the with block.
        """
        if not self.is_locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
        """
        self.release()


class filelocker(object):
    def __init__(self, filepath, lock_name=None):
        self.filepath = filepath
        self.lock_name = lock_name

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            if self.filepath in FileLock.lock_manifest:
                kwargs[self.lock_name] = None
                f(*args, **kwargs)
            else:
                with FileLock(self.filepath) as lock:
                    kwargs[self.lock_name] = lock
                    f(*args, **kwargs)

        return wrapper


class datafile_modifier(object):
    def __init__(self, data_util):
        self.data_util = data_util

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            if self.data_util.DATA_FILE in FileLock.lock_manifest:
                f(*args, **kwargs)
            else:
                with FileLock(self.data_util.DATA_FILE):
                    self.data_util.load()
                    f(*args, **kwargs)
                    self.data_util.save()

        return wrapper


def persisted_data_modifier(f):
    def wrapped_f(cls, *args, **kwargs):
        if os.path.abspath(cls._DATA_FILE) in FileLock.lock_manifest:
            f(cls, *args, **kwargs)
        else:
            with FileLock(cls._DATA_FILE):
                cls._load()
                f(cls, *args, **kwargs)
                cls._save()
    return wrapped_f


class MetaDataFileUtil(type):
    @property
    def _DATA_FILE(cls):
        raise NotImplementedError

    @property
    def _persisted_data(cls):
        raise NotImplementedError

    def _load(cls):
        if os.path.exists(cls._DATA_FILE):
            with open(cls._DATA_FILE) as data_file:
                json_data = data_file.read()
                if json_data:
                    cls._persisted_data = json.loads(json_data)

    def _save(cls):
        with open(cls._DATA_FILE, "w") as data_file:
            json.dump(cls._persisted_data, data_file)


def shell(command, capture=False, ignore_errors=False):
    out_stream = sys.stdout
    err_stream = sys.stderr
    if capture:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE

    p = subprocess.Popen(command, shell=True, stdout=out_stream, stderr=err_stream)
    (out, err) = p.communicate()

    if p.returncode != 0 and not ignore_errors:
        print "the shell encountered an error (return code %s) while executing '%s'" % (p.returncode, command)
        raise

    return out


def virtualenv(command, ignore_errors=False):
    virtualenv_dir = os.path.join(env.project_path, "virtualenv")
    if not os.path.exists(virtualenv_dir):
        shell("virtualenv --no-site-packages " + virtualenv_dir)
    shell("source " + virtualenv_dir + "/bin/activate && " + command, ignore_errors=ignore_errors)
