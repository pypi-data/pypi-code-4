# -*- coding: utf-8 -*-

import hashlib

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    UnicodeText,
    )
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint

__all__ = ['UserModel', 'UserModelMixin']


def get_password_digest(password):
    return hashlib.sha1(password).hexdigest()


class UserModelMixin(object):
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password_digest = Column(String(255))

    def set_password(self, password):
        self.password_digest = get_password_digest(password)

    password = property(fset=set_password)

    def verify_password(self, password):
        return self.password_digest == get_password_digest(password)

    def __repr__(self):
        return "<%s.%s username=%r>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.username)
