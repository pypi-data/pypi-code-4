# -*- coding: utf-8 -*-

from pyramid_layout.panel import panel_config
from pyramid import security


@panel_config('login_menuitem', renderer="procyon:templates/panels/login_menuitem.jinja2")
def login_menuitem_panel(context, request):
    return {
        'userid': security.authenticated_userid(request),
        'login_url': request.route_url('login'),
        'logout_url': request.route_url('logout'),
        }
