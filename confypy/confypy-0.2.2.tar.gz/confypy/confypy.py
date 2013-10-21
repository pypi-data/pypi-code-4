from collections import deque
from .loaders import load_file
from .loaders import load_env_path
from .loaders import load_env_keys
from .loaders import load_locations
from .loaders import load_python
from .loaders import load_env_python
from .parsers import parser_from_parser_or_filename


class AttributeDict(dict):
    '''
    Pulled directly from lexicon:
    https://pypi.python.org/pypi/lexicon
    https://github.com/bitprophet/lexicon
    '''
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def __getitem__(self, key):
        '''
        Not included from lexicon. We want everything returned
        from an attribute dict to also return an attribute dict
        if it's a dict
        '''
        result = dict.__getitem__(self, key)

        try:
            return AttributeDict(result)
        except (TypeError, ValueError):
            return result


class Location(object):

    @classmethod
    def from_python(cls, path, parser=None):
        obj = Location(path, loader=load_python, parser=parser)
        return obj

    @classmethod
    def from_env_python(cls, path, parser=None):
        obj = Location(path, loader=load_env_python, parser=parser)
        return obj

    @classmethod
    def from_path(cls, path, parser=None):
        parser = parser_from_parser_or_filename(parser, path)
        obj = Location(path, loader=load_file, parser=parser)
        return obj

    @classmethod
    def from_env_path(cls, key, parser=None):
        value = load_env_keys((key,))
        parser = parser_from_parser_or_filename(parser, value[key])
        obj = Location(key, loader=load_env_path, parser=parser)
        return obj

    @classmethod
    def from_env_keys(cls, keys, parser=None):
        obj = Location(keys, loader=load_env_keys, parser=parser)
        return obj

    @classmethod
    def from_dict(cls, value, parser=None):
        obj = Location(value, parser=parser)
        return obj

    def __init__(self, value, loader=None, parser=None):
        self.value = value
        self.loader = loader
        self.parser = parser

    def load(self):
        data = self.loader(self.value) if self.loader else self.value
        return self.parser(data) if self.parser else data


class ConfigData(object):
    ''' ConfigData is effectively a simplified, read-only, ChainMap'''

    def __init__(self, maps):
        self.maps = maps

    def get(self, key, default=None):
        try:
            return self.value_for_key(key)
        except KeyError:
            return default

    def __getattr__(self, key):

        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        result = self.value_for_key(key)

        try:
            return AttributeDict(result)
        except (TypeError, ValueError):
            return result

    def value_for_key(self, key):
        maps = self.maps
        for each in maps:
            try:
                return each[key]
            except KeyError:
                pass

        raise KeyError(key)


class Config(object):
    def __init__(self, defaults=None, chain=False):
        self.defaults = {} if defaults is None else defaults
        self.chain = chain
        self.locations = []

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = self.load()
            return self._data

    def extend(self, config):
        self.data.maps.append(config)

    def load(self):
        if self.chain:
            return self.load_chain(self.locations)
        else:
            return self.load_first(self.locations)

    def load_chain(self, locations):
        data = deque()
        data.append(self.defaults)
        [data.appendleft(x) for x in load_locations(locations)]

        return ConfigData(data)

    def load_first(self, locations):
        data = deque()
        for x in load_locations(locations):
            data.append(x)
            return ConfigData(data)

        data.append(self.defaults)
        return ConfigData(data)


class ConfigManager(object):
    pass
