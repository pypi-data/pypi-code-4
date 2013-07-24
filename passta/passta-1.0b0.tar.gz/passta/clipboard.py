import os
import subprocess
from itertools import chain


class ClipboardError(Exception): pass


def which(name):
    for dir_ in os.environ.get('PATH', '').split(os.pathsep):
        filename = os.path.join(dir_, name)
        if os.path.exists(filename) and os.access(filename, os.X_OK):
            yield filename


def copy(text):
    for filename in chain(which('xclip'), which('pbpaste')):
        p = subprocess.Popen([filename, '-i'], stdin=subprocess.PIPE)
        p.communicate(text.encode('utf-8'))
        break
    else:
        raise ClipboardError(
            'no cli clipboard interface found (xclip or pbpaste required)')
