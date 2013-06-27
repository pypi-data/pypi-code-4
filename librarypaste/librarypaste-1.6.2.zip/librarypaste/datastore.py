#!/usr/bin/env python
# encoding: utf-8
"""
datastore.py

Created by Chris Mulligan on 2010-05-09.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
from __future__ import print_function

import sys
import uuid
import importlib
import abc
from string import letters, digits
from random import choice

def shortkey():
    firstlast = list(letters + digits)
    middle = firstlast + list('-_')
    return ''.join((choice(firstlast), choice(middle), choice(middle),
        choice(middle), choice(firstlast)))

def init_datastore(config):
    """
    Take the config definition and initialize the datastore.

    The config must contain either a 'datastore' parameter, which
    will be simply returned, or
    must contain a 'factory' which is a callable or entry
    point definition. The callable should take the remainder of
    the params in config as kwargs and return a DataStore instance.
    """
    if 'datastore' in config:
        # the datastore has already been initialized, just use it.
        return config['datastore']
    factory = config.pop('factory')
    if isinstance(factory, basestring):
        "a string like 'package.module:Class.classmethod'"
        module_name, _, factory_name = factory.partition(':')
        module = importlib.import_module(module_name)
        factory = eval(factory_name, module.__dict__)
    return factory(**config)

class DataStore(object):
    """
    Abstract base class describing a datastore backend.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def _store(self, uid, content, data):
        """
        Store the given dict of content at uid. Nothing returned.
        """

    @abc.abstractmethod
    def _storeLog(self, nick, time, uid):
        """
        Adds the nick & uid to the log for a given time/order. No return.
        """

    @abc.abstractmethod
    def _retrieve(self, uid):
        """
        Return a dict with the contents of the paste, including the raw
        data, if any, as the key 'data'. Must pass in uid, not shortid.
        """

    @abc.abstractmethod
    def lookup(self, nick):
        """
        Looks for the most recent paste by a given nick.
        Return the uid or None
        """

    @abc.abstractmethod
    def _lookupUid(self, short_uid):
        """
        Given a short UID, return the equivalent long UID.
        """

    @abc.abstractmethod
    def list(self):
        """
        Generate all stored UIDs.
        """

    def store(self, type, nick, time, fmt=None, code=None, filename=None,
            mime=None, data=None, makeshort=True):
        """
        Store code or a file. Returns a tuple containing the uid and shortid
        """
        uid = str(uuid.uuid4())
        if makeshort:
            shortid = shortkey()
        else:
            shortid = None

        temp = {'uid': uid, 'shortid': shortid, 'type': type, 'nick': nick,
            'time': time,
            'fmt': fmt, 'code': code,
            'filename': filename, 'mime': mime}
        paste = dict(
            (k, v) for (k, v) in temp.iteritems() if v
        )
        self._store(uid, paste, data)
        if nick:
            self._storeLog(nick, time, uid)
        return (uid, shortid)

    def retrieve(self, id):
        """Retrieve a paste. Returns a dictionary containing all metadata
        and the file data, if it's a file."""
        if len(id) < 10:
            shortid = id
            uid = self._lookupUid(shortid)
        else:
            uid = id
        return self._retrieve(uid)

    @staticmethod
    def migrate(dest_datastore, source_datastore):
        """
        Copy all records from source_datastore to dest_datastore
        """
        for uid in source_datastore.list():
            try:
                paste = source_datastore._retrieve(uid)
            except Exception as exc:
                print(
                    "{exc.__class__.__name__} occurred retrieving {uid}: {exc}"
                    .format(**vars()),
                    file=sys.stderr)
                continue
            data = paste.pop('data', None)
            try:
                dest_datastore._store(uid, paste, data)
            except Exception as exc:
                print("{exc.__class__.__name__} occurred storing {uid}: {exc}"
                    .format(**vars()),
                    file=sys.stderr)
                continue
