#coding:utf-8

class Cache(object):
    def get(self, key):
        raise NotImplementedError()

    def set(self, key, value):
        raise NotImplementedError()
