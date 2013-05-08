from .base import _base


class Client(object):

    def __init__(self, host, port, api_key, is_secure=False):
        self.data = {'host': host, 'port': port, 'headers': {'Api-Key': api_key}, 'is_secure': is_secure}

    def __getattr__(self, namespace):
        self.data.update(namespace=namespace)
        return type('Request', (object, _base), self.data)()
