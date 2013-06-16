# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import six

class SimpleMap(object):
    """
    A simple ``dict`` wrapper . It mainly prevents its inner ``dict`` from overriding existing keys and lazy deletion.
    """

    def __init__(self, *args):
        self._map = dict()

    def set(self, key, value):
        """
        Sets a key/value pair. If the key already exist, a ``KeyError`` gets thrown.

        :param key:
        :type key: \*
        :param value:
        :type value: \*
        :raises: KeyError

        """
        if key in self._map:
            raise KeyError('Key "%s" is already taken. "SimpleMap" does not allow to override keys.' % key)
        self._map[key] = value

    def remove(self, key):
        """
        Removes a key/value pair based upon the given *key*. If the key doesn't exist, a ``KeyError`` gets thrown.

        :param key:
        :type key: \*

        :raises: KeyError

        """
        if not key in self._map:
            raise KeyError('Key "%s" does not exist. "SimpleMap" does not allow to lazily delete non-existing keys.' % key)
        del self._map[key]

    def has(self, key):
        """
        Returns whether a key exists.

        :param key:
        :type key: \*

        :rtype: bool
        """

        return key in self._map

    def get(self, key):
        """
        Returns the value for *key* if present, else ``None``.

        :param key:
        :type key: \*

        :rtype: \* or None
        """
        return self._map.get(key, None)

    def values(self, *keys):
        """
        Returns a list of values for the related *\*keys*. If *\*keys* is empty, all values get returned.

        :param \*keys:
        :type \*keys: list of keys

        :rtype: list
        """

        if len(keys) < 1:
            return six.itervalues(self._map)
        return [value for key, value in six.iteritems(self._map) if key in keys]

    def keys(self):
        """
        Returns a list of all keys.

        :rtype: list
        """
        return six.iterkeys(self._map)


    def length(self):
        """
        Returns the number of items in this map.

        :rtype: int
        """
        return len(self._map)