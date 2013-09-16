#-*- coding: utf-8 -*-
import config
import qiniu.rs
import qiniu.rsf
import qiniu.conf
from termcolor import colored

class Remove():
    def __init__(self, config_path, prefix):
        config_instance = config.Config(config_path)

        self.prefix = prefix
        self.bucket_name = config_instance.get_bucket_name()

        qiniu.conf.ACCESS_KEY = str(config_instance.get_access_key())
        qiniu.conf.SECRET_KEY = str(config_instance.get_secret_key())

    def _get_files(self):
        rets, err = qiniu.rsf.Client().list_prefix(
            self.bucket_name, prefix = self.prefix
        )
        return [ret['key'] for ret in rets['items']]

    def run(self):
        files = self._get_files()
        if files:
            print(colored('Removing remote files...', 'magenta'))
            for file_key in files:
                ret, error = qiniu.rs.Client().delete(self.bucket_name, file_key)
                if error is not None:
                    print(colored('Remote file %s removed failed' % file_key, 'red'))
                else:
                    print('Remote file %s removed successful' % file_key)