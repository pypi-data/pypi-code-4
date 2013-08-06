
from __future__ import absolute_import

import redis
from . import BaseBackend

local_pool = redis.ConnectionPool()

class RedisBackend(BaseBackend):
    def __init__(self, pool=local_pool):
        self.client = redis.Redis(connection_pool=pool)

    def set(self, key, value, expiration=None, commit=True):
        result = self.client.set(key, value)
        if expiration:
            self.client.expire(key, expiration)
        if not result:
            raise AttributeError("can't set attribute")
        return result

    def get(self, key, default=None):
        value = self.client.get(key)
        if value is None:
            return default
        return value

    def delete(self, key, commit=True):
        return self.client.delete(key)

class RedisHashedBackend(BaseBackend):
    def __init__(self, pool=local_pool, key=''):
        self.client = redis.Redis(connection_pool=pool)
        self.key = key

    def set(self, key, value, expiration=None, commit=True):
        result = self.client.hset(self.key, key, value)
        #if not result:
        #raise AttributeError("can't set attribute")
        return result

    def get(self, key, default=None):
        value = self.client.hget(self.key, key)
        if value is None:
            return default
        return value

    def delete(self, key, commit=True):
        return self.client.hdel(self.key, key)

