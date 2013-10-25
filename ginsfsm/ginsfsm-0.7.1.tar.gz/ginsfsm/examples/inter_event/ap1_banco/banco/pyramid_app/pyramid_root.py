# -*- encoding: utf-8 -*-
"""
applic10
=======

Applic 10

"""
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.security import (
    Allow,
    Authenticated,
    Everyone,
    DENY_ALL,
)

from ginsfsm.gobj import GObj
from ginsfsm.c_timer import GTimer


#----------------------------------------------------------------------#
#                           Applic1
#----------------------------------------------------------------------#

#-------------------------------------------#
#               Actions
#-------------------------------------------#
def ac_timeout(self, event):
    self.config.counter += 1
    self.send_event(self.timer, 'EV_SET_TIMER', seconds=self.config.seconds)


PYRAMIDROOT_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT', ac_timeout, 'ST_IDLE'),
        ),
    }
}

PYRAMIDROOT_GCONFIG = {
    'pyramid_router_url': [
        str, '', 0, None,
        'pyramid url to start the router'
    ],
    'seconds': [int, 60, 0, None, "Timer to increment the counter."],
    'counter': [int, 0, 0, None, "Counter to display."],
}


class PyramidRoot(GObj):
    """  Root resource (/)

    .. ginsfsm::
       :fsm: PYRAMIDROOT_FSM
       :gconfig: PYRAMIDROOT_GCONFIG

    *Input-Events:*
        * :attr:`'EV_TIMEOUT'`: Timer over.

    """
    __acl__ = [
        (Allow, Everyone, 'view'),
        (DENY_ALL),
    ]

    def __init__(self):
        GObj.__init__(self, PYRAMIDROOT_FSM, PYRAMIDROOT_GCONFIG)

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.pyramid_router_url:
            self.gaplic.start_up_router(
                pyramid_router_url=self.config.pyramid_router_url,
                pyramid_root=self
            )

        self.timer = self.create_gobj(
            None,       # unnamed gobj
            GTimer,     # gclass
            self        # parent
        )
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=self.config.seconds)


#-------------------------------------------#
#               Views
#-------------------------------------------#
@view_config(
    context=PyramidRoot,
    permission='view',
    renderer='templates/mytemplate.pt')
def default_view(self, request):
    return {'project': 'banco'}
