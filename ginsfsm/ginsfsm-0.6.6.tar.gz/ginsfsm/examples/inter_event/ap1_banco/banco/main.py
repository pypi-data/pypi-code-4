# -*- encoding: utf-8 -*-
"""
banco
=====

It uses :class:`ginsfsm.protocols.wsgi.server.c_wsgi_server.GWsgiServer`.

.. autofunction:: main

"""

from ginsfsm.gaplic import GAplic
from ginsfsm.globals import (
    set_global_app,
    set_global_main_gaplic,
)
from ginsfsm.protocols.wsgi.server.c_wsgi_server import GWsgiServer
from banco.pyramid_app import pyramid_wsgi_app
from banco.ac_cuentas import Cuentas


#===============================================================
#       Paste app's factory.
#       To run with gserve banco.ini
#===============================================================
def pyramid_paste_factory(global_config, **local_conf):
    """ Returns the WSGI application.
    """
    return pyramid_wsgi_app(global_config, **local_conf)


#===============================================================
#                   Main
#===============================================================
def main(global_config, **local_conf):
    """ Entry point to run with gserve (PasteDeploy)
    """
    if 'application' in local_conf:
        application = local_conf.pop('application')
    else:
        raise Exception('You must supply a wsgi application in local_conf.')

    if 'gaplic_name' in local_conf:
        gaplic_name = local_conf.pop('gaplic_name')
    else:
        raise Exception('You must supply a gaplic name in local_conf.')

    ga = GAplic(
        name=gaplic_name,
        roles=('banco',),
        **local_conf)
    set_global_main_gaplic(ga)
    ga.create_gobj(
        'wsgi_server',
        GWsgiServer,
        ga,
        application=application,
    )
    ga.create_gobj(
        'cuentas',
        Cuentas,
        ga,
        __unique_name__=True,
    )
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print("<<<     To test the application, go to http://localhost:8001   >>>")
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    return ga


if __name__ == "__main__":
    """ You can run directly this file as main, without gserve.
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # simulate running from ini file
    local_conf = {
        'gaplic_name': 'main_gaplic',
        'application': 'wsgi-application',
        'GWsgiServer.host': '0.0.0.0',
        'GWsgiServer.port': 8001,
        'GSock.trace_dump': False,
        'GObj.trace_mach': False,
        'GObj.trace_creation': False,
        'GObj.trace_traverse': False,
        'GObj.trace_subscription': False,

        'GObj.logger': logging,
        'PyramidRoot.pyramid_router_url': '__pyramid_router__',
        'GRouter.trace_router': True,

        'GRouter.static_routes':
        'RobberA, financiera+bolsa+publicidad, http://localhost:8002;',
    }

    ga = main({}, **local_conf)

    pyramid_settings = {
        'gaplic': 'main_gaplic',
        'pyramid.reload_templates': True,
        'pyramid.debug_authorization': False,
        'pyramid.debug_notfound': False,
        'pyramid.debug_routematch': False,
        'pyramid.debug_templates': True,
        'pyramid.default_locale_name': 'en',
    }

    set_global_app(
        'wsgi-application',
        pyramid_paste_factory({}, **pyramid_settings)
    )

    try:
        ga.start()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
