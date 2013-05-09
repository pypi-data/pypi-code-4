# -*- encoding: utf-8 -*-
"""
publicidad
==========

It uses :class:`ginsfsm.protocols.wsgi.server.c_wsgi_server.GWsgiServer`.

.. autofunction:: main

"""

from ginsfsm.gaplic import GAplic
from ginsfsm.globals import (
    set_global_main_gaplic,
)
from publicidad.c_sorteo import GSorteo


#===============================================================
#                   Main
#       Paste app factory.
#       To run with gserve publicidad.ini
#===============================================================
def main(global_config, **local_conf):
    """ Entry point to run with gserve (PasteDeploy)
    """
    if 'gaplic-name' in local_conf:
        gaplic_name = local_conf.pop('gaplic-name')
    else:
        raise Exception('You must supply an gaplic name ("gaplic-name")')

    ga = GAplic(
        name=gaplic_name,
        roles=('publicidad',),
        **local_conf)
    set_global_main_gaplic(ga)

    ga.create_gobj(
        'sorteo',
        GSorteo,
        ga,
        __unique_name__=True,
    )
    return ga


if __name__ == "__main__":
    """ You can run directly this file, without gserve.
    """
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # simulate running from ini file
    local_conf = {
        'gaplic-name': 'publicidad',
        'router_enabled':  True,
        'GRouter.server':  True,
        'GRouter.localhost_route_ports':  8002,
        'GRouter.trace_router':  True,
        'GObj.trace_mach':  True,
        'GObj.trace_creation':  False,
        'GObj.trace_traverse':  True,
        'GObj.trace_subscription':  False,
        'GSock.trace_dump':  True,
    }
    ga = main({}, **local_conf)

    try:
        ga.start()
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')
