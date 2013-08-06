
from ..core import SimpleCacheObject
from ..backend.redis import RedisBackend, local_pool

_common_backends = {}

def get_redis_object(pool):
    def backend_generator():
        global _common_backends

        backend = _common_backends.get(pool, None)
        if not backend:
            backend = _common_backends[pool] = RedisBackend(pool)
        return backend

    class RedisObject(SimpleCacheObject):
        _backend_generator = staticmethod(backend_generator)

    return RedisObject

LocalRedisObject = get_redis_object(local_pool)

def get_redis_hashed_object(pool, key):
    def backend_generator():
        global _common_backends

        backend = _common_backends.get(pool, None)
        if not backend:
            backend = _common_backends[pool] = RedisHashedBackend(pool, key)
        return backend

    class RedisHashedObject(SimpleCacheObject):
        _backend_generator = staticmethod(backend_generator)

    return RedisHashedObject

def LocalRedisHashedObject(key):
    return get_redis_hashed_object(local_pool, key)
