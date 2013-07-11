################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import ConfigParser
from fs.osfs import OSFS
from fs.s3fs import S3FS
from fs.sftpfs import SFTPFS
from pp.core.logger import LOG

class Filesystems(object):

    def __init__(self, configuration):
        self._fs = dict()
        self._configuration = configuration
        self.configure()

    def configure(self):
        self.cp = ConfigParser.ConfigParser()
        self.cp.read([self._configuration])
        for section in self.cp.sections():
            self._fs[section] = None
            continue
            fs_type = self.option_get(cp, section, 'type')
            configurator= getattr(self, 'configure_%s' % fs_type, None)
            if configurator is None:
                raise ValueError('Unsupported fs type "%s"' % fs_type)
            configurator(cp, section)

    def option_get(self, section, key):
        if not self.cp.has_option(section, key):
            raise ValueError('Missing "%s.%s"' % (section, key))
        return self.cp.get(section, key)

    def configure_osfs(self, section):
        """ Configure local filesystem layer """

        root_directory = self.option_get(section, 'root')
        self._fs[section] = OSFS(root_directory, 
                                 thread_synchronize=True,
                                 create=True)
        LOG.info('Configured osfs "%s"' % section)

    def configure_s3fs(self, section):
        """ Configure Amazon S3 layer """

        from boto.s3.connection import S3Connection

        key = self.option_get(section, 'key')
        secret = self.option_get(section, 'secret')
        bucket = self.option_get(section, 'bucket')
        create_bucket = False
        if self.cp.has_option(section, 'create_bucket'):
            create_bucket = self.cp.getboolean(section, 'create_bucket')
        if create_bucket:
            conn = S3Connection(key, secret)
            conn.create_bucket(bucket)
            LOG.info('Created S3 bucket "%s"' % bucket)
        self._fs[section] = S3FS(bucket,
                                 aws_access_key=key,
                                 aws_secret_key=secret,
                                 thread_synchronize=True)
        LOG.info('Configured s3fs "%s"' % section)

    def configure_sftpfs(self, section):
        """ Configure SFTPFS layer """

        host = self.option_get(section, 'host')
        root_directory = self.option_get(section, 'root')
        self._fs[section] = SFTPFS(host,
                                   root_directory)
        LOG.info('Configured sftpfs "%s"' % section)

    def configure_dropboxfs(self, section):
        """ Configure Dropbox-FS layer """

        from pp.core.fs_dropbox import dropboxfs_factory

        app_key = self.option_get(section, 'app_key')
        app_secret = self.option_get(section, 'app_secret')
        username = self.option_get(section, 'username')
        password = self.option_get(section, 'password')
        self._fs[section] = dropboxfs_factory(app_key,
                                              app_secret,
                                              username,
                                              password)
        LOG.info('Configured dropboxfs "%s"' % section)

    def __getitem__(self, key):
        """ Access a filesystem layer through [] notation """

        if not key in self._fs:
            raise KeyError('No filesystem "%s" found' % key)
        # lazy configuration of the filesystem layers
        if self._fs[key] is None:
            fs_type = self.option_get(key, 'type')
            configurator = getattr(self, 'configure_%s' % fs_type, None)
            if configurator is None:
                raise ValueError('Unsupported fs type "%s"' % fs_type)
            configurator(key)
        return self._fs[key]

if __name__ == '__main__':
    import sys
    fs = Filesystems(sys.argv[1])
    src = fs['localfs']
    target = fs['aws']
    print src.listdir()
    print target.listdir()

    for fn in src.listdir():
        print fn
        fp = target.open(fn, 'wb')
        fp.write(src.open(fn, 'rb').read())
        fp.close()
