import fuse
from errno import ENOENT
import stat
from time import time

fuse.fuse_python_api = (0, 2)

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = stat.S_IFDIR | 0755
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 2
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 4096
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0


class DeployFuse(fuse.Fuse):
    def __init__(self, *a, **kw):
        fuse.Fuse.__init__(self, *a, **kw)

    def getattr(self, path):
        print 'called getattr:', path
        if path == '/':
            st = MyStat()
            st.st_atime = int(time())
            st.st_mtime = st.st_atime
            st.st_ctime = st.st_atime
            return st
        else:
            return -ENOENT

if __name__ == '__main__':
    server = DeployFuse(
            version='deploy-fuse')
            #'test',
            #foreground=True, nothreads=True)
    server.parse(errex=1)
    server.main()
