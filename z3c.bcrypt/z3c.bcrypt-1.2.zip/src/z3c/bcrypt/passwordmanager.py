##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Password Managers using bcrypt or pbkdf2 encoding.
"""

from zope.interface import implements
from zope.password.interfaces import IPasswordManager
from cryptacular import bcrypt, pbkdf2

MAXLENGTH = 4096

class BcryptPasswordManager(object):
    """bcrypt password manager.
    """

    implements(IPasswordManager)

    def __init__(self):
        self._manager = bcrypt.BCRYPTPasswordManager()

    def encodePassword(self, password, salt=None):
        return self._manager.encode(password)

    def checkPassword(self, encoded_password, password):
        return self._manager.check(encoded_password, password[:MAXLENGTH])

class PBKDF2PasswordManager(BcryptPasswordManager):
    """pbkdf2 password manager.
    """

    def __init__(self):
        self._manager = pbkdf2.PBKDF2PasswordManager()
