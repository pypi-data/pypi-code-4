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
Auth Views
"""

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget, authenticated_userid

from webhelpers.html import literal
from webhelpers.html import tags

import formencode
from pyramid_simpleform import Form
from ..forms.simpleform import FormRenderer

import edbob
from ..db import Session
from rattail.db.auth import authenticate_user, set_user_password


def forbidden(request):
    """
    Access forbidden view.

    This is triggered whenever access is not allowed for an otherwise
    appropriate view.
    """

    msg = literal("You do not have permission to do that.")
    if not authenticated_userid(request):
        msg += literal("&nbsp; (Perhaps you should %s?)" %
                       tags.link_to("log in", request.route_url('login')))
    request.session.flash(msg, allow_duplicate=False)

    url = request.referer
    if not url or url == request.current_route_url():
        url = request.route_url('home')
    return HTTPFound(location=url)


class UserLogin(formencode.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    username = formencode.validators.NotEmpty()
    password = formencode.validators.NotEmpty()


def login(request):
    """
    The login view, responsible for displaying and handling the login form.
    """

    referrer = request.get_referrer()

    # Redirect if already logged in.
    if request.user:
        return HTTPFound(location=referrer)

    form = Form(request, schema=UserLogin)
    if form.validate():
        user = authenticate_user(Session(),
                                 form.data['username'],
                                 form.data['password'])
        if user:
            request.session.flash("%s logged in at %s" % (
                    user.display_name,
                    edbob.local_time().strftime('%I:%M %p')))
            headers = remember(request, user.uuid)
            return HTTPFound(location=referrer, headers=headers)
        request.session.flash("Invalid username or password")

    url = edbob.config.get('edbob.pyramid', 'login.logo_url',
                           default=request.static_url('edbob.pyramid:static/img/logo.jpg'))
    kwargs = eval(edbob.config.get('edbob.pyramid', 'login.logo_kwargs',
                                   default="dict(width=500)"))

    return {'form': FormRenderer(form), 'referrer': referrer,
            'logo_url': url, 'logo_kwargs': kwargs}


def logout(request):
    """
    View responsible for logging out the current user.

    This deletes/invalidates the current session and then redirects to the
    login page.
    """

    request.session.delete()
    request.session.invalidate()
    headers = forget(request)
    referrer = request.get_referrer()
    return HTTPFound(location=referrer, headers=headers)


class CurrentPasswordCorrect(formencode.validators.FancyValidator):

    def _to_python(self, value, state):
        user = state
        if not authenticate_user(Session, user.username, value):
            raise formencode.Invalid("The password is incorrect.", value, state)
        return value


class ChangePassword(formencode.Schema):

    allow_extra_fields = True
    filter_extra_fields = True

    current_password = formencode.All(
        formencode.validators.NotEmpty(),
        CurrentPasswordCorrect())

    new_password = formencode.validators.NotEmpty()
    confirm_password = formencode.validators.NotEmpty()

    chained_validators = [formencode.validators.FieldsMatch(
            'new_password', 'confirm_password')]


def change_password(request):
    """
    Allows a user to change his or her password.
    """

    if not request.user:
        return HTTPFound(location=request.route_url('home'))

    form = Form(request, schema=ChangePassword, state=request.user)
    if form.validate():
        set_user_password(request.user, form.data['new_password'])
        return HTTPFound(location=request.get_referrer())

    return {'form': FormRenderer(form)}


def add_routes(config):
    config.add_route('login',           '/login')
    config.add_route('logout',          '/logout')
    config.add_route('change_password', '/change-password')
    

def includeme(config):
    add_routes(config)

    config.add_forbidden_view(forbidden)

    config.add_view(login, route_name='login',
                    renderer='/login.mako')

    config.add_view(logout, route_name='logout')

    config.add_view(change_password, route_name='change_password',
                    renderer='/change_password.mako')
