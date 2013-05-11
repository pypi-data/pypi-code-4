# -*- encoding: utf-8 -*-
"""
Pyramid App
===========

"""
from pyramid.config import Configurator

from ginsfsm.globals import (
    set_global_app,
    get_global_app,
)

from banco.pyramid_app.pyramid_root import PyramidRoot


#-------------------------------------------------#
#       Paste entry point
#       Pyramid wsgi-app configuration
#-------------------------------------------------#
def pyramid_wsgi_app(global_config, **local_conf):
    """ Returns a WSGI application.
    """
    if 'gaplic' in local_conf:
        gaplic_name = local_conf.pop('gaplic')
    else:
        raise Exception('You must supply a gaplic name in ini file.')

    gaplic = get_global_app(gaplic_name)
    if not gaplic:
        raise Exception("gaplic '%s' supplied for wsgi is invalid" %
                        gaplic_name)

    config = Configurator(
        root_factory=get_root,
        settings=local_conf,
    )
    config.add_static_view(
        'static',
        'banco:pyramid_app/static',
        cache_max_age=3600
    )

    # Set up sockjs views
    config.include("ginsfsm.protocols.sockjs.server")

    # Set up views
    config.scan("banco.pyramid_app")

    # Now we have the gaplic and the config for make the root
    make_root(gaplic, config)

    return config.make_wsgi_app()


#----------------------------------------------------------------------#
#                           Pyramid root
#----------------------------------------------------------------------#
app_root = None


def make_root(gaplic, config):
    global app_root
    if app_root is None:
        app_root = gaplic.create_gobj(
            None,   # pyramid resources tree root MUST be unnamed.
            PyramidRoot,
            None    # and must have no parent.
        )
        set_global_app('banco_app', app_root)
    return app_root


def get_root(request):
    return app_root
