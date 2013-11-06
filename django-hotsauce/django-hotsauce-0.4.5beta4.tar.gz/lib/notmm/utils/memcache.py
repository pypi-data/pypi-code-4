"""Memcached support tools 

Copyright 2010-2012 Etienne Robillard <erob@gthcfoundation.org>
All rights reserved.

<LICENSE=ISC>
"""

from __future__ import absolute_import
import memcache

__all__ = ['MemcacheStore']

class MemcacheStore(memcache.Client):
    """Simple wrapper over ``memcache.Client`` to encapsulate Django
    settings logic.

    Obtain a default ``memcache.Client`` object by looking up memcached
    server settings with the provided ``settings`` module argument ::

    .. coding: Python

        >>> from notmm.utils.django_settings import LazySettings
        >>> mc = MemcacheStore(settings=LazySettings())
        >>> repr(mc)
        <MemcacheStore: 'xxx'>
    """
    
    def __init__(self, settings, key_value='default'):
        self.settings = settings
        self.netloc = settings.CACHE_BACKEND_LOCATION
        super(MemcacheStore, self).__init__([self.netloc,], debug=settings.DEBUG)
    
    def __repr__(self):
        return "<MemcacheStore: %s>" % self.settings

