#!/usr/bin/env python3

"""Module providing the AttributesMixIn class."""


class AttributesMixIn(object):

    """Mix-in, providing an attributes collection of variable type.

    Collection type may be list, set or dict.  Getters and setters are
    polymorphic.


    To return a node's inherited attributes, access
    self.all_attributes.  The return value depends on the attribute
    type self was initialized with (defaults to dict).

        1. dict - Returns a dict with self's attributes presiding over
        its ancestors.

        2. list - Returns a list containing all attributes of all
        ancestors, starting with root.

    """

    def __init__(self, attr_type, **kwargs):
        """Initialized with one of dict, list, or set."""
        super().__init__(**kwargs)
        if attr_type is None:
            self.attributes = None
        else:
            ## The ._collector method will be used to recursively
            ## compose the attributes for a node.  The ._selector
            ## tests if an item exists as attribute and returns a bool
            ## or, if attr_type is dict the attribute value.
            self.attributes = attr_type()
            if attr_type is list:
                self._collector = list.extend
                self._selector = list.__contains__
            elif attr_type is dict:
                self._collector = dict.update
                self._selector = dict.get
            elif attr_type is set:
                self._collector = set.union
                self._selector = set.__contains__
            else:
                raise AttributeError('Invalid attribute type.')

    def get_attribute(self, key, default=None):
        """Returns value if attributes collection is dict, otherwise
        True, if key is present else False."""
        if self.attributes is None:
            return None
        else:
            val = self._selector(self.attributes, key)
            return val if not val is None else default

    def has_attribute(self, key):
        """True if self.attributes includes key."""
        return self.get_attribute(key) is not None

    def get_attribute_else(self, key, fn):        
        """Returns attribute for key, if present, else calls fn(self)."""
        if self.attributes is None:
            return None
        else:
            val = self._selector(self.attributes, key)
            return val if not val is None else fn(self)

    def add_attributes(self, attrs):
        """Adds attrs to self.attributes."""
        if self.attributes is None:
            raise AttributeError('self has no attributes collection.')
        else:
            self._collector(self.attributes, attrs)
    
