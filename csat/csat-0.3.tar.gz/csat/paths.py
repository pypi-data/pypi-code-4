import re
import os


class PathWalker(object):

    def __init__(self, base, fullpath=False):
        self.base = base
        self.prefix_length = len(self.base) + 1 if not fullpath else 0
        self.filters = {
            'filename': [],
            'directory': []
        }

    def filter(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._add_filter(k, True, v)
        return self

    def exclude(self, **kwargs):
        for k, v in kwargs.iteritems():
            self._add_filter(k, False, v)
        return self

    def _add_filter(self, chain, include, pattern):
        regex = re.compile('^' + pattern + '$')
        self.filters[chain].append((include, regex))

    def _check_include(self, chain, value):
        for is_filter, f in self.filters.get(chain, []):
            matched = bool(f.match(value))
            if is_filter ^ matched:
                #print('{} filtered out by {}'.format(value, f.pattern))
                return False

        return True

    def _listdir(self, base):
        for f in os.listdir(base):
            full = os.path.join(base, f)
            if os.path.isdir(full):
                if self._check_include('directory', f):
                    for f in self._listdir(full):
                        yield f
            else:
                if self._check_include('filename', f):
                    yield full[self.prefix_length:]

    def walk(self):
        return self._listdir(self.base)
