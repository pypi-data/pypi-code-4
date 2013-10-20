#======================================
# pathutil.py
# Date: 26 May 2011
# Author: Sergey Mikhtonyuk
#======================================
import os
import errno
import shutil

try:
    WindowsError
except NameError:
    WindowsError = None

#===========================================================

class Error(EnvironmentError):
    pass

#===========================================================

def makedirs(path, mode=0777):
    ''' Fixes os.makedirs throw on all directories exist '''
    try:
        os.makedirs(path, mode)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

#===========================================================

def listdir_recursive(path):
    ''' Lists all content of path recursively, breadth-first, including folders '''
    def ld_rec(path, prefix, ret):
        for l in os.listdir(path):
            ll = os.path.join(prefix, l)
            lp = os.path.join(path, l)
            ret.append(ll)
            if os.path.isdir(lp):
                ld_rec(lp, ll, ret)

    ret = []
    ld_rec(path, '', ret)
    return ret

#===========================================================

def copytree(src, dst, symlinks=False):
    ''' Same copytree with fixed makedirs '''
    makedirs(dst)
    errors = []
    for name in os.listdir(src):
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                shutil.copy2(srcname, dstname)
        except Error, err:
            errors.extend(err.args[0])
        except EnvironmentError, why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)

#===========================================================

class path_tree(object):
    def __init__(self, paths):
        self.paths = paths

    def listdir(self, path=None, normalize=True):
        return [n if normalize else p for p, n in self.listdirx(path)]

    def listdirx(self, path=None):
        if not path:
            path = ''
        return [(p, os.path.normpath(p)) for p in self.paths if os.path.dirname(os.path.normpath(p)) == path]

#===========================================================
