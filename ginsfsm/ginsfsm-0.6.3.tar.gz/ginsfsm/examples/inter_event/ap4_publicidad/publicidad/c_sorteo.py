# -*- encoding: utf-8 -*-
""" GSorteo GObj

.. autoclass:: GSorteo
    :members: start_up

"""

from ginsfsm.gobj import GObj
from ginsfsm.c_timer import GTimer


def ac_regalo(self, event):
    """ Event attributes:
        * :attr:`sorteo`: .

    """
    user_name = event.user_name

    if event.__intra_event__:
        origin_gaplic = event.__intra_event__.origin_gaplic
        origin_role = event.__intra_event__.origin_role
        origin_gobj = event.__intra_event__.origin_gobj
        self.user_sorteo[user_name] = {
            'gaplic': origin_gaplic,
            'role': origin_role,
            'gobj': origin_gobj
        }

    self.set_timeout(3)


def ac_sorteo(self, event):
    self.broadcast_event('EV_REGALO', regalo="Premio gordo!!")
    self.set_timeout(3)


GSORTEO_FSM = {
    'event_list': (
        'EV_REGALO:top input output',
        'EV_TIMEOUT:bottom input',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_REGALO',      ac_regalo,      None),
            ('EV_TIMEOUT',     ac_sorteo,      None),
        ),
    }
}

GSORTEO_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class GSorteo(GObj):
    """  GSorteo GObj.
    A Sample gobj.

    .. ginsfsm::
       :fsm: GSORTEO_FSM
       :gconfig: GSORTEO_GCONFIG

    *Input-Events:*
        * :attr:`'EV_REGALO'`: sample input event.

          Event attributes:

              * ``data``: sample event attribute.

    *Output-Events:*
        * :attr:`'EV_REGALO_ACK'`: sample output event.

          Event attributes:

              * ``data``: sample event attribute.

    """
    def __init__(self):
        GObj.__init__(self, GSORTEO_FSM, GSORTEO_GCONFIG)
        self.user_sorteo = {}

    def start_up(self):
        """ Initialization zone.
        """
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
            timeout_event_name='EV_TIMEOUT',
        )
        self.set_timeout(3)

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)
