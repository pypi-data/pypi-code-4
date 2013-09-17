#-*- coding: utf-8 -*-
import os
import config
import qiniu.io
import qiniu.rs
import qiniu.conf
import platform
from common import print_color

class Upload():
    def __init__(self, path, config_path):
        config_instance = config.Config(config_path)

        self.path = os.path.abspath(path)
        self.bucket_name = config_instance.get_bucket_name()

        qiniu.conf.ACCESS_KEY = str(config_instance.get_access_key())
        qiniu.conf.SECRET_KEY = str(config_instance.get_secret_key())

    def _get_files(self):
        if not os.path.exists(self.path):
            return None

        if os.path.isfile(self.path):
            return [self.path]

        if os.path.isdir(self.path):
            result = []
            for root, dirs, files in os.walk(self.path):
                result += [os.path.join(root, file_path) for file_path in files]
            return result

        return None

    def _get_file_key(self, file_path):
        if platform.system().lower() == 'windows':
            return os.path.normpath(file_path).replace('\\', '_').replace(':', '')

        return file_path.replace('/', '_')[1:]

    def run(self):
        files = self._get_files()
        if files:
            print_color('Uploading local files...', 'magenta')
            for file_path in files:
                file_key = self._get_file_key(file_path)
                uptoken = qiniu.rs.PutPolicy(
                    '%s:%s' % (self.bucket_name, file_key)
                ).token()
                ret, error = qiniu.io.put_file(
                    uptoken, file_key, file_path
                )
                if error is not None:
                    print_color('File %s uploaded failed' % file_path, 'red')
                else:
                    print('File %s uploaded successful' % file_path)
