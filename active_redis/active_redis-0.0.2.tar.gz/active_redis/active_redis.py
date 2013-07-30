import redis

class ActiveRedis(object):
    _connexion = None

    @classmethod
    def connexion(cls):
        if cls._connexion is None:
            pool = redis.ConnectionPool(**cls.config.get('connexion', {}))
            cls._connexion = redis.Redis(connection_pool=pool)
        return cls._connexion


