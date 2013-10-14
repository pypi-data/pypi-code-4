import os
import subprocess
from itertools import chain


class ClipboardError(IOError):
    pass


def which(name):
    '''
    Find all binaries of given name in path.

    >>> env = which('env')
    >>> env
    <generator object which at 0x...>
    >>> list(env)
    ['/usr/bin/env']

    '''
    for dir_ in os.environ.get('PATH', '').split(os.pathsep):
        filename = os.path.join(dir_, name)
        if os.path.exists(filename) and os.access(filename, os.X_OK):
            yield filename


def copy(text):
    '''Copy text to clipboard; uses xclip or pbpaste.'''
    for filename in chain(which('xclip'), which('pbcopy')):
        p = subprocess.Popen([filename], stdin=subprocess.PIPE)
        p.communicate(text.encode('utf-8'))
        if p.returncode:
            raise ClipboardError(
                '{} returned with exit code {}'.format(filename, p.returncode))
        return
    raise ClipboardError(
        'no cli clipboard interface found (xclip or pbpaste required)')
