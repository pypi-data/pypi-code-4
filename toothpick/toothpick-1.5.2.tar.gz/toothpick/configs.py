'''
Toothpick provides several configuration structs for conveninent initialization
of resources.  Simply instantiate one of these in your app, and then pass it
into the appropriate `register()` decorator call on your model.

These objects are read-only inside toothpick, and are safe to re-use across
multiple `register()` decorator calls.
'''

class Config(object): pass # for grouping

class HTTPConfig(Config):
    def __init__(self, base_url='', username=None, password=None):
        self.base_url = base_url
        self.username = username
        self.password = password

    def __repr__(self):
        return self.base_url


class MongoConfig(Config):
    def __init__(self,
                 host='localhost',
                 port=None,
                 database='default',
                 username=None,
                 password=None):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def __repr__(self):
        rep = self.host
        if self.port:
            rep += ":%s" % self.port
        rep += "/%s" % self.database
        return rep

class FileConfig(Config):
    def __init__(self, abspath):
        self.abspath = abspath

    def __repr__(self):
        return self.abspath
