# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute

from procyon.base.interfaces import IBaseModel


class IUserModel(IBaseModel):
    id = Attribute("The primary key")
    username = Attribute("The user name")
    password_digest = Attribute("A digest of the password")
    password = Attribute("A write-only property to set the password")

    def set_password(self, password):
        """Set the password"""

    def verify_password(self, password):
        """Verify the given password"""
