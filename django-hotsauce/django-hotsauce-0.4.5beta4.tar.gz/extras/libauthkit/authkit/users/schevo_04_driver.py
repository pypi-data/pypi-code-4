#!/usr/bin/env python
# -*- coding: utf-8 -*-
# schevo_04_driver.py
# Copyright (C) 2010 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
#
# <LICENSE=ISC>

#default base class to use for extending with custom 
#authentication methods
from authkit.users import Users

__all__ = ['ManagerBase', 'UserManagerBase']

class ManagerBase(Users):
    """
    Creates a composite proxy object for the User Entity. 

    >>> manager = ManagerBase(db.User)
    >>> user = manager.objects.get(username="erob")
    >>> user
    <User account: "Etienne Robillard">
    >>> user.username == "erob"
    True
    """

    # Keep this for compatibility with Pylons ;-)
    api_version = 0.4

    def __init__(self, data, encrypt=None):
        super(ManagerBase, self).__init__(data, encrypt=encrypt)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'objects'):
            raise AttributeError('%r is missing required objects attribute'%cls)
        new_obj = object.__new__(cls)
        new_obj._default_manager = cls.objects
        return new_obj

class UserManagerBase(ManagerBase):
    def user_exists(self, username):
        #look up the user
        user_object = self.objects.get(username=username)
        if user_object is not None:
            return True
        return False

    def user_has_password(self, username, password):
        u = self.objects.get(username=username)
        if u.f.password.compare(password):
            return True
        return False
    
    ### Roles and Groups permissions
    #def role_exists(self, roles):
    #    # return True if the roles exists
    #    return False
