#!/usr/bin/env python
# encoding: utf-8
"""
jsonstore.py
"""

import re
import os
import time
import datetime
import json

from datastore import DataStore

class JsonDataStore(DataStore):
    """Stores using json encoded into files"""
    def __init__(self, repo):
        super(JsonDataStore, self).__init__()
        self.repo = repo
        if not os.path.exists(repo):
            os.mkdir(repo)
        self.shortids = {}

    def _store(self, uid, content, data=None):
        content['time'] = time.mktime(content['time'].timetuple())
        fd = open(os.path.join(self.repo, uid), 'wb')
        fd.write(json.dumps(content))
        fd.close()
        if data:
            with open(os.path.join(self.repo, '%s.raw' % uid), 'wb') as fd:
                fd.write(data)
        try:
            self.shortids[content['shortid']] = uid
            with open(os.path.join(self.repo, 'shortids.txt'), 'a') as f:
                f.write('%s %s\n' % (content['shortid'], uid))
        except KeyError:
            pass

    def _storeLog(self, nick, time, uid):
        with open(os.path.join(self.repo, 'log.txt'), 'a') as f:
            f.write('%s %s\n' % (nick, uid))

    def lookup(self, nick):
        last = None
        for line in open(os.path.join(self.repo, 'log.txt')):
            who, uid = line.strip().rsplit(None, 1)
            if who == nick:
                last = uid
        return last

    def _lookupUid(self, shortid):
        try:
            uid = self.shortids[shortid]
        except KeyError:
            for line in open(os.path.join(self.repo, 'shortids.txt')):
                l1, l2 = line.strip().rsplit(None, 1)
                self.shortids[l1] = l2
        try:
            uid = self.shortids[shortid]
        except KeyError:
            uid = None
        return uid

    def _retrieve(self, uid):
        with open(os.path.join(self.repo, uid), 'rb') as f:
            val = f.read()
        if not val:
            raise ValueError("empty paste")
        paste = json.loads(val)
        if paste.get('type', None) == 'file':
            with open(os.path.join(self.repo, '%s.raw' % uid), 'rb') as f:
                paste['data'] = f.read()
        paste.setdefault('type', 'file' if paste.get('data') else 'code')
        paste['time'] = datetime.datetime.fromtimestamp(paste['time'])
        return paste

    def list(self):
        uid_pattern = re.compile(
            '^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')
        return (name
            for name in os.listdir(self.repo)
            if uid_pattern.match(name)
        )
