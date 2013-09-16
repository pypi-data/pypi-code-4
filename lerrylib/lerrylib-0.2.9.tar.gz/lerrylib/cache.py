#!/usr/bin/python
# -*- coding: utf-8 -*-
import _envi
CACHE_DICT = {}

class InterCache(object):
    def __init__(self, cache_dict):
        self.cache = cache_dict

    def get(self, k):
        return self.cache.get(k)

    def get_list(self, key_li):
        return [self.get(i) for i in key_li]

    def get_dict(self, key_li):
        result = {}
        for i in key_li:
            result[i] = self.get(i)
        return result

    def set(self, k, v):
        self.cache[k] = v

    def delete(self, k):
        try:
            del self.cache[k]
        except KeyError:
            pass

cache = InterCache(CACHE_DICT)

        
if __name__ == '__main__':
    pass
