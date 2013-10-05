import datetime

class MemoryBackend(object):
    """ The memeory backend acts as a class suitible for testing or very simple
    uses. Not intended for production use. In theory it should work for single
    process executions. """

    def store(self, key, value, expire=None, adapter=None):
        if expire is not None:
            if not isinstance(expire, datetime.datetime):
                raise AttributeError("Expiry time must be a datetime object")
        self.__dict__[key] = (value, expire)

    def expire(self, key, adapter=None):
        del self.__dict__[key]

    def get(self, key, adapter=None):
        val = self.__dict__[key]
        # Check if data has expired or has an expiry at all
        if val[1] is not None and val[1] < datetime.datetime.now():
            self.expire(key)
            return

        return val[0]

    def __getitem__(self, key):
        return self.get(key)

class FlaskSessionBackend(object):
    """ This backend allows interfacing with Flask sessions """

    def store(self, key, value, expire=None, adapter=None):
        from flask import session
        if expire is not None:
            if not isinstance(expire, datetime.datetime):
                raise AttributeError("Expiry time must be a datetime object")
        session[key] = (value, expire)

    def expire(self, key, adapter=None):
        from flask import session
        del session[key]

    def expire_all(self, prefix="", adapter=None):
        from flask import session
        for key in session.keys():
            if key.startswith(prefix):
                del session[key]

    def get(self, key, adapter=None):
        from flask import session
        val = session[key]
        # Check if data has expired or has an expiry at all
        try:
            if val[1] is not None and val[1] > datetime.datetime.now():
                self.expire(key)
                return

            return val[0]
        except TypeError:
            return

    def __getitem__(self, key):
        return self.get(key)
