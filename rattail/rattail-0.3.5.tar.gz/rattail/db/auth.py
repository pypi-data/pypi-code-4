#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Authentication & Authorization
"""

import bcrypt
from .model import User, Role


def authenticate_user(session, username, password):
    """
    Attempt to authenticate a user.

    :returns: A :class:`.model.User` instance, if successful.  Otherwise
       returns ``None``.
    """

    user = session.query(User)\
        .filter_by(username=username)\
        .first()
    if user and bcrypt.hashpw(password, user.salt) == user.password:
        return user
    return None


def set_user_password(user, password):
    """
    Set a user's password.
    """

    user.salt = bcrypt.gensalt()
    user.password = bcrypt.hashpw(password, user.salt)


def special_role(session, uuid, name):
    """
    Fetches, or creates, a "special" role.
    """

    role = session.query(Role).get(uuid)
    if not role:
        role = Role(uuid=uuid, name=name)
        session.add(role)
    return role


def administrator_role(session):
    """
    Returns the "Administrator" role.
    """

    return special_role(session, 'd937fa8a965611dfa0dd001143047286', 'Administrator')


def guest_role(session):
    """
    Returns the "Guest" role.
    """

    return special_role(session, 'f8a27c98965a11dfaff7001143047286', 'Guest')


def grant_permission(role, permission):
    """
    Grant a permission to a role.
    """

    # TODO: Make this a `Role` method (or make `Role.permissions` a `set` so we
    # can do `role.permissions.add('some.perm')` ?).
    if permission not in role.permissions:
        role.permissions.append(permission)


def has_permission(session, principal, permission, include_guest=True):
    """
    Determine if a principal has been granted a permission.

    :param session: A SQLAlchemy session instance.

    :param principal: May be either a :class:`.model.User` or
       :class:`.model.Role` instance.  It is also expected that this may
       sometimes be ``None``, in which case the "Guest" role will typically be
       assumed.

    :param permission: The full internal name of a permission,
       e.g. ``'users.create'``.

    :param include_guest: Whether or not the "Guest" role should be included
       when checking permissions.  If ``False``, then Guest's permissions will
       *not* be consulted.

    Note that if no ``principal`` is provided, and ``include_guest`` is set to
    ``False``, then no checks will actually be done, and the return value will
    be ``False``.
    """

    if hasattr(principal, 'roles'):
        roles = list(principal.roles)
    elif principal is not None:
        roles = [principal]
    else:
        roles = []

    # Admin always has permission.
    admin = administrator_role(session)
    if admin in roles:
        return True

    if include_guest:
        roles.append(guest_role(session))
    for role in roles:
        for perm in role.permissions:
            if perm == permission:
                return True
    return False
