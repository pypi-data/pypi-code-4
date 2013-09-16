#-*- coding:utf-8 -*-
from json import load

class Config():
    def __init__(self, fileName):
        with file(fileName) as fp:
            self.configs = load(fp)

    def _get_key(self, key):
        return self.configs[key] if self.configs and self.configs.has_key(key) else None

    def get_access_key(self):
        return self._get_key('access_key')

    def get_secret_key(self):
        return self._get_key('secret_key')

    def get_bucket_name(self):
        return self._get_key('bucket_name')
