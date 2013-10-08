
class BaseManager(object):

    def __init__(self, namespace):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def length(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def exists(self):
        raise NotImplementedError
