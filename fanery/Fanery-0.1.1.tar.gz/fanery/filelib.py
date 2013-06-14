from os.path import abspath, realpath, normpath, curdir, splitext
from os.path import isfile, isdir, exists
from os.path import basename as filename
from os.path import getsize as filesize
from os.path import dirname as filedir
from os.path import join as joinpath
from os import listdir

def files(*args, **argd):
    return dict((f.name, f) for f in args + argd.values() if isfile(f))

def fullpath(path):
    return normpath(realpath(abspath(path)))
