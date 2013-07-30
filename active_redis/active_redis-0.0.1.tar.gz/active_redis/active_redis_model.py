from pluralize_engine import PluralizeEngine

class ActiveRedisModel(object):

    @classmethod
    def find_all(cls):
        objects = []
        for key in cls.all_redis_keys():
            obj = cls.find_by_redis_key(key)
            objects.append(obj)
        return objects

    @classmethod
    def find(cls, uuid):
        return cls.find_by_redis_key(cls.redis_namespace_with_uuid(uuid))

    @classmethod
    def find_by_redis_key(cls, redis_key):
        return cls(**ActiveRedis.connexion().hgetall(redis_key))

    def value_of(self, attr_name):
        return getattr(self, attr_name)() if \
                       callable(getattr(self, attr_name)) else \
                       getattr(self, attr_name)

    def save(self):
        data = {'uuid': self.uuid}
        for attr_name in self.stored_attrs:
            data[attr_name] = self.value_of(attr_name)
        ActiveRedis.connexion().hmset(self.redis_namespace_with_uuid(data['uuid']),
                                      data)
        return data['uuid']

    def update_attr(self, attr_name, value):
        return ActiveRedis.connexion().hset(
                    self.redis_namespace_with_uuid(self.uuid), attr_name, value)

    def delete(self):
        return ActiveRedis.connexion().delete(
                    self.redis_namespace_with_uuid(self.uuid))

    @classmethod
    def pluralize_model_name(cls):
        return PluralizeEngine.pluralize(cls.__name__).lower()

    @classmethod
    def count(cls):
        return len(cls.all_redis_keys())

    @classmethod
    def delete_all(cls):
        for key in cls.all_redis_keys():
            ActiveRedis.connexion().delete(key)
        return True

    @classmethod
    def all_redis_keys(cls):
        return ActiveRedis.connexion().keys('{}:*'.format(cls.redis_namespace()))

    @classmethod
    def redis_namespace_with_uuid(cls, uuid):
        return '{}:{}'.format(cls.redis_namespace(), uuid)

    @classmethod
    def redis_namespace(cls):
        pluralized_model_name = cls.pluralize_model_name()
        namespace_prefix = ActiveRedis.config.get('namespace_prefix', None)
        if namespace_prefix is not None:
            return '{}:{}'.format(namespace_prefix, pluralized_model_name)
        else:
            return '{}'.format(pluralized_model_name)


