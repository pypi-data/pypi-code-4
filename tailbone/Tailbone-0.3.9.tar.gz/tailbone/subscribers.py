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
Event Subscribers
"""

from pyramid import threadlocal
import rattail
from . import helpers

from pyramid.security import authenticated_userid
from .db import Session
from rattail.db.model import User
from rattail.db.auth import has_permission


def before_render(event):
    """
    Adds goodies to the global template renderer context.
    """

    request = event.get('request') or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals['h'] = helpers
    renderer_globals['url'] = request.route_url
    renderer_globals['rattail'] = rattail


def context_found(event):
    """
    Attach some goodies to the request object.

    The following is attached to the request:

    * The currently logged-in user instance (if any), as ``user``.

    * A shortcut method for permission checking, as ``has_perm()``.

    * A shortcut method for fetching the referrer, as ``get_referrer()``.
    """

    request = event.request

    request.user = None
    uuid = authenticated_userid(request)
    if uuid:
        request.user = Session.query(User).get(uuid)

    def has_perm(perm):
        return has_permission(Session(), request.user, perm)
    request.has_perm = has_perm

    def has_any_perm(*perms):
        for perm in perms:
            if has_permission(Session(), request.user, perm):
                return True
        return False
    request.has_any_perm = has_any_perm

    def get_referrer(default=None):
        if request.params.get('referrer'):
            return request.params['referrer']
        if request.session.get('referrer'):
            return request.session.pop('referrer')
        referrer = request.referrer
        if not referrer or referrer == request.current_route_url():
            if default:
                referrer = default
            else:
                referrer = request.route_url('home')
        return referrer
    request.get_referrer = get_referrer


def includeme(config):
    config.add_subscriber(before_render, 'pyramid.events.BeforeRender')
    config.add_subscriber(context_found, 'pyramid.events.ContextFound')
