#!/usr/bin/env python
"""Generic user model for authkit based on top of Schevo (Durus)."""

from notmm.dbapi.orm import XdserverProxy, RelationProxy
from authkit.users.schevo_04_driver import UserManagerBase

__all__ = ['UserBase', 'User']

class UserBase(UserManagerBase):
    def __init__(self, dbname='accounts'):
        self.db = XdserverProxy(dbname)
        self.objects = RelationProxy(db.User)

class User(UserBase): pass

