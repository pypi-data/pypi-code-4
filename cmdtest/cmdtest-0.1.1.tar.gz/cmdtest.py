import os
from functools import wraps
from subprocess import Popen, PIPE
from shutil import rmtree
from tempfile import mkdtemp, mkstemp
from contextlib import contextmanager
from time import time, sleep
import shlex

# this one for us
import attest

# this one for our users
from attest import *

class Dir(object):
    def __init__(self, path):
        self.path = path

d = Dir(None)

class TimeoutError(Exception):
    pass

@contextmanager
def tempdir(*args, **kwargs):
    path = mkdtemp(*args, **kwargs)
    try:
        yield path
    finally:
        rmtree(path)

def withfile(path):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            fullpath = os.path.abspath(path)
            with File(path=fullpath) as f:
                return func(f, *args, **kwargs)
        return wrapped
    return wrapper

class File(object):
    def __init__(self, text='', name=None, path=None):
        self.path = os.path.abspath(path) if path else None
        self.name = name
        self.text = text

    def __enter__(self):
        assert self.exists
        return self

    def __exit__(self, *args):
        pass

    def create(self):
        if not self.path:
            _, self.path = mkstemp(dir=d.path)
            with open(self.path, 'w') as f:
                f.write(self.text)

    def __str__(self):
        return self.path if self.path else ''

    def exists(self):
        try:
            thepath = self.path if self.path else os.path.join(d.path, self.name)
            f = open(thepath)
        except IOError:
            return False
        else:
            if self.text:
                s = f.read()
                f.close()
                return s == self.text
            return True

class NonExistentFile(object):
    def __init__(self):
        self.path = None

    def __str__(self):
        return self.path if self.path else ''

    def exists(self):
        return False

    def create(self):
        self.path = 'not_a_file'


def create_options(options):
    for o in options:
        try:
            o.create()
        except AttributeError:
            pass

class Result(object):
    def __init__(self, program, options, timeout, input):
        self.timeout = timeout
        create_options(options)
        arguments = [str(o) for o in options]

        cmd = shlex.split(program) + list(arguments)
        print cmd
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=d.path)
        p.stdin.write(input)
        p.stdin.flush()
        p.stdin.close()
        start_time = time()
        while p.poll() is None:
            if time() > start_time + self.timeout:
                p.kill()
                raise TimeoutError()
            sleep(0.01)
        self.out = p.stdout.read()
        self.err = p.stderr.read()
        self.status = p.returncode

    def __lshift__(self, o):
        print o
        assert False
        return self

def test(meth):
    @wraps(meth)
    def wrapper(self):
        global d
        with tempdir() as d.path:
            meth(self)
    return attest.test(wrapper)

class Program(attest.Tests):
    def __init__(self, path, **kargs):
        attest.Tests.__init__(self, **kargs)
        self.path = path

    def __call__(self, *args, **kargs):
        _timeout = kargs.get('_timeout', 0.1)
        _in = kargs.get('_in', '')
        return Result(self.path, args, _timeout, _in)

    def test(self, func):
        @wraps(func)
        def wrapper():
            global d
            with tempdir() as d.path:
                func()
        return super(Program, self).test(wrapper)

