# -*- coding: utf-8 -*-

from pyramid_layout.panel import panel_config


@panel_config('flash', renderer="procyon:templates/panels/flash.jinja2")
def flash_panel(context, request, queue=''):
    return {
        'messages': request.session.pop_flash(queue),
        }
