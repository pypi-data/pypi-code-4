"""
Create a dictionary-like object from a resource prefix.
"""

from whiff import gateway

class ResourceDictionary:
    def __init__(self, env, pathPrefix):
        self.env = env
        self.pathPrefix = list(pathPrefix)
    def keyPath(self, key):
        path = self.pathPrefix + [key];
        return path
    def __getitem__(self, key):
        path = self.keyPath(key)
        env = self.env
        return gateway.getResource(env, path)
    def get(self, key, default=None):
        path = self.keyPath(key)
        env = self.env
        return gateway.getResource(env, path, default)
    def __setitem__(self, key, value):
        path = self.keyPath(key)
        env = self.env
        return gateway.putResource(env, path, value)
    def keys(self):
        "Aggregate operations will only work if pathPrefix gives 'directory contents'"
        path = self.pathPrefix
        sequence = gateway.getResource(env, path)
        return list(sequence)
    def values(self):
        ks = self.keys()
        return [ self[k] for k in ks ]
    def items(self):
        ks = self.keys()
        return [ (k, self[k]) for k in ks ]
    def childDictionary(self, key):
        # return item as dictionary (no existence test)
        return ResourceDictionary(self.env, self.keyPath(key))
        
