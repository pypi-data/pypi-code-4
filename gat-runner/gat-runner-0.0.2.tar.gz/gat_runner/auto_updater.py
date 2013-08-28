from distutils.version import StrictVersion
import os
from shutil import copy2
from urllib2 import urlopen
import zipfile

import inspect
def s(template, **kwargs):
    '''Usage: s(string, **locals())'''
    if not kwargs:
        frame = inspect.currentframe()
        try:
            kwargs = frame.f_back.f_locals
        finally:
            del frame
        if not kwargs:
            kwargs = globals()
    return template.format(**kwargs)


def colorize(message, color='blue'):
  color_codes = dict(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37)
  code = color_codes.get(color, 34)
  msg = '\033[%(code)sm%(message)s\033[0m' % {'code':code, 'message':message}
  # print(msg)
  return msg


class AutoUpdater(object):
    def __init__(self, dirpath=None):
        if not dirpath:
            self.dirpath = os.path.dirname(os.path.realpath(__file__))
        else:
            self.dirpath = dirpath

    def get_os(self):
        from sys import platform as _platform
        if _platform == "linux" or _platform == "linux2":
            return 'linux'
        elif _platform == "darwin":
            return 'mac'
        elif _platform == "win32":
            return 'windows'

    def download_file(self, filename, url, timeout=10):
        data = urlopen(url, timeout=timeout).read()
        fo = open(s('{self.dirpath}/downloaded_{filename}'), 'w')
        fo.write(data)
        fo.close()

    def update_file(self, filename):
        original_file = s('{self.dirpath}/{filename}')
        backuped_file = s('{self.dirpath}/{filename}.bak')
        downloaded_file = s('{self.dirpath}/downloaded_{filename}')
        if os.path.exists(original_file):
            copy2(original_file, backuped_file)
        copy2(downloaded_file, original_file)

    def install_zip_file(self, filename):
        if filename.endswith('.zip'):
            original_file = s('{self.dirpath}/{filename}')
            zfile = zipfile.ZipFile(original_file)
            for name in zfile.namelist():
                (dirname, filename) = os.path.split(name)
                if dirname and not os.path.exists(dirname):
                    os.mkdir(dirname)
                fd = open(name, 'w')
                fd.write(zfile.read(name))
                fd.close()

    def rollback_updated_file(self, filename):
        backuped_file = s('{self.dirpath}/{filename}.bak')
        if os.path.exists(backuped_file):
            copy2(backuped_file, s('{self.dirpath}/{filename}'))

    def remove_downloaded_file(self, filename):
        downloaded_file = s('{self.dirpath}/downloaded_{filename}')
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

    def has_new_version(self, current_version, latest_version_url, timeout=1):
        try:
            latest_version = urlopen(latest_version_url, timeout=1).read()
            result = StrictVersion(latest_version) > StrictVersion(current_version)
            if result:
                print(colorize('New version available (%s). Your version: %s' % (latest_version, current_version), color='blue'))
            else:
                print(colorize('Your version (%s) is up to date.' % current_version, color='white'))
            return result
        except Exception as e:
            print(colorize('Error on verify new version. (%s)' % (str(e),), color='red'))
            return None

    def auto_update(self, files, timeout=10):
        "files = {filename: url}"
        try:
            for filename, url in list(files.items()):
                # print(filename, url)
                self.download_file(filename, url, timeout=timeout)
        except Exception as e:
            print(colorize('Auto update failed because a download error. (%s)' % str(e), color='red'))
            return

        try:
            for filename, url in list(files.items()):
                # print(filename)
                self.update_file(filename)
                self.install_zip_file(filename)
            print(colorize('Update successfully', color='green'))
            for filename, url in list(files.items()):
                self.remove_downloaded_file(filename)
        except Exception as e:
            import sys
            raise e, None, sys.exc_info()[2]
            for filename, url in list(files.items()):
                self.rollback_updated_file(filename)
            print(colorize('Update error. (%s)' % (str(e)), color='red'))

