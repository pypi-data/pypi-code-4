#!/usr/bin/env python
# coding=utf-8

"""
defines the Record class
"""

from .base import *


class Record(object):
    """a record is a simple object with these attribute:

    It represents a record in cloudns system.

    =======  ======================================================
    attr     description
    =======  ======================================================
    rid      record id
    type     record type
    name     DNS label
    content  DNS value
    isp      tel or uni for China Telecom and China Unicom
    ctime    last modification timestamp
    z        zone name
    ttl      DNS TTL
    prio     MX priority, default is 0
    status   this is returned from server. 0 means PENDING_ACTIVE,
             1 means ACTIVE, 2 means PENDING_REMOVAL.
    =======  ======================================================

    """
    RESERVED_ATTRIBUTES = ('rid', 'name', 'type', 'content', 'isp',
                           'ctime', 'z', 'ttl', 'prio', 'status')

    def __init__(self, **kwargs):
        self._params = kwargs

    def __getattr__(self, name):
        if name in self.RESERVED_ATTRIBUTES:
            return self._params.get(name)
        raise AttributeError

    def __setattr__(self, name, value):
        if name in self.RESERVED_ATTRIBUTES:
            raise CloudnsBadUsage(u'use Record.update() to set new values.')
        return super(Record, self).__setattr__(name, value)

    def __str__(self):
        return str(self._params)

    def update(self, **kwargs):
        """return a new Record with given values replaced.

        allowed keys:
            z, name, content, isp, type, ttl

        rid is not allowed here, because it is used to locate which record to
        update.

        """
        params = dict(self._params)
        for k, v in kwargs.items():
            if v is not None:
                params[k] = v
        return Record(**params)

    def as_dict(self):
        # return a copy of it. Record itself is read-only.
        return dict(self._params)
