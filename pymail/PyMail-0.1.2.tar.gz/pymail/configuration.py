'''
Module configuration
====================

Contains the Configuration class
'''

import yaml
from .debug import D
import logging

class DictMapper(object):
    '''
    Helper class for accessing configuration values as object attributes
    '''
    def __init__(self, dictObj):
        '''
        Create DictMapper object

        The object's attribute dictionary is set from the dictionary provided.

        :param dict dictObj: dictionary
        '''
        assert type(dictObj) is dict
        self.__dict__ = dictObj

    def __getattribute__(self, name):
        '''
        Return attribute

        If the attribute to be returned is a dictionary, a DictMapper object is returned instead.
        '''
        if name == '_':
            return object.__getattribute__(self, '__dict__')
        o = object.__getattribute__(self, name)
        if type(o) is dict:
            return DictMapper(o)
        return o

    def __repr__(self):
        '''
        Return repr
        '''
        return str(object.__getattribute__(self, '__dict__'))

    def __call__(self, key, default=None):
        '''
        Get element by key, providing a default

        :param key:
        :param default:
        :return: element at key, or default if not found, or None if no default

        Returns an element by key, or a default which can be provided as an optional second argument.
        '''
        return object.__getattribute__(self, '__dict__').get(key, default)

    def has(self, key):
        '''
        Check whether key exists

        :param string key:

        This method is the same as the `has_key` methods for dictionaries, just with a name more pleasing to me.
        '''
        return object.__getattribute__(self, '__dict__').has_key(key)

    def __iter__(self):
        return object.__getattribute__(self, '__dict__').iterkeys()

    def dict(self, key):
        return object.__getattribute__(self, key)

class Configuration(DictMapper):
    '''
    Contains the configuration

    This class provides configuration values as object attributes instead of dictionary __dict__ents. The configuration can be
    accessed like::

        value = config.dir.entry

    instead of the more awkward::

        value = config['dir]['entry']

    '''
    def __init__(self, configFile):
        '''
        Create Configuration object

        :param string configFile: path to configuration file
        '''
        config = yaml.load(file(configFile)) or {}
        super(Configuration, self).__init__(config)
