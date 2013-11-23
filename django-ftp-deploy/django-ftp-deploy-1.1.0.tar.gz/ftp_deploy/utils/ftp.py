import os
from ftplib import FTP

from .decorators import check


class ftp_connection(object):
    """FTP Connection helper. Provide methods to manage ftp resources"""
    def __init__(self, host, username, password, ftp_path):
        self.host = host
        self.username = username
        self.password = password
        self.ftp_path = self.encode(ftp_path)
        self.connected = 0

    def connect(self):
        """Initialize FTP Connection"""
        self.ftp = FTP(self.host)
        self.ftp.login(self.username, self.password)
        self.connected = 1

    def create_file(self, file_path, content):
        """Create file populated with 'content' and save to 'file_path' location"""
        file_path = self.encode(file_path)
        self.ftp.storbinary('STOR ' + self.ftp_path + file_path, content)

    def remove_file(self, file_path):
        """Remove file from 'file_path' location, and clear empty directories"""
        file_path = self.encode(file_path)
        self.ftp.delete(self.ftp_path + file_path)

        dirname = file_path.split(os.sep)
        for i in xrange(len(dirname)):
            current = os.sep.join(dirname[:-1 - i])
            try:
                self.ftp.rmd(self.ftp_path + current)
            except Exception, e:
                return False

    def make_dirs(self, file_path):
        """ Create FTP tree directories based on 'file_path'"""
        file_path = self.encode(file_path)
        dirname = os.path.dirname(file_path).split(os.sep)
        for i in xrange(len(dirname)):
            current = os.sep.join(dirname[:i + 1])
            try:
                self.ftp.dir(self.ftp_path + current)
            except Exception, e:
                self.ftp.mkd(self.ftp_path + current)

    def encode(self, content):
        """Encode path string"""
        return str(content).encode('ascii', 'ignore')

    def quit(self):
        """Close FTP Connection"""
        return self.ftp.quit() if self.connected else False


class ftp_check(ftp_connection):

    """Check FTP Connection, return True if fail"""

    @check('FTP')
    def check_ftp_login(self):
        self.connect()

    @check('FTP')
    def check_ftp_path(self):
        self.ftp.cwd(self.ftp_path)
        self.ftp.cwd('/')

    def check_all(self):

        status = self.check_ftp_login()
        if status[0] == True:
            return status

        status = self.check_ftp_path()
        if status[0] == True:
            return status

        return False, ''

