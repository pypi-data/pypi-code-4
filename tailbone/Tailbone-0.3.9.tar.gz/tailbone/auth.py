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

from zope.interface import implementer
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone, Authenticated

from .db import Session
from rattail.db.model import User
from rattail.db.auth import has_permission


@implementer(IAuthorizationPolicy)
class TailboneAuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        for userid in principals:
            if userid not in (Everyone, Authenticated):
                user = Session.query(User).get(userid)
                if user:
                    return has_permission(Session(), user, permission)
        if Everyone in principals:
            return has_permission(Session(), None, permission)
        return False

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError
