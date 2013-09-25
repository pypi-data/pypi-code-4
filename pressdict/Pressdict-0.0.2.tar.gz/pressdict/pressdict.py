import zlib
import json


sentinel = object()


class Pressdict(object):
    """Compressed key-value store for JSON-serializable objects."""

    def __init__(self):
        self.d = {}
        self.compress = lambda obj: zlib.compress(json.dumps(obj))
        self.decompress = lambda string: json.loads(zlib.decompress(string))

    def __iter__(self):
        for key in self.d:
            yield key

    def __len__(self):
        return len(self.d)

    def __contains__(self, key):
        return key in self.d

    def __getitem__(self, key):
        return self.decompress(self.d[key])

    def __delitem__(self, key):
        del self.d[key]

    def __setitem__(self, key, value):
        self.d[key] = self.compress(value)

    def __repr__(self):
        return repr(dict((key, self.decompress(value))
            for key, value in self.d.iteritems()))

    def clear(self):
        return self.d.clear()

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        for key, value in self.d.iteritems():
            yield key, self.decompress(value)

    def iterkeys(self):
        for key in self.d.iterkeys():
            yield key

    def itervalues(self):
        for value in self.d.itervalues():
            yield self.decompress(value)

    def keys(self):
        return self.d.keys()

    def pop(self, key, default=sentinel):
        if default is sentinel:
            return self.decompress(self.d.pop(key))
        else:
            try:
                return self.decompress(self.d.pop(key))
            except KeyError:
                return default

    def values(self):
        return list(self.itervalues())
