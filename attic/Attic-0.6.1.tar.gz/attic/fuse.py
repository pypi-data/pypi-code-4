import llfuse
import sys


class AtticOperations(llfuse.Operations):
    """
    """
    def __init__(self):
        super(AtticOperations, self).__init__()
        print('__init__')

    def statfs(self):
        print('statfs')
        stat_ = llfuse.StatvfsData()
        return stat_

    def access(self, inode, mode, ctx):
        print('access')
        return True

    def getattr(self, inode):
        print('getattr', inode)

    def forget(self, inode_list):
        print('forget', inode_list)

    def lookup(self, parent_inode, name):
        print('lookup')

    def open(self, inode, flags):
        print('open')

    def opendir(self, inode):
        print('opendir')

    def read(self, fh, off, size):
        print('read')

    def readdir(self, fh, off):
        print('readdir')

    def readlink(self, inode):
        print('readlink')

    def release(self, fh):
        print('release')

    def releasedir(self, fh):
        print('releasedir')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: %s <mountpoint>' % sys.argv[0])

    operations = AtticOperations()
    llfuse.init(operations, sys.argv[1], ['fsname=atticfs', 'nonempty'])
    try:
        llfuse.main(single=True)
    except:
        llfuse.close(unmount=False)
        raise
    llfuse.close()
