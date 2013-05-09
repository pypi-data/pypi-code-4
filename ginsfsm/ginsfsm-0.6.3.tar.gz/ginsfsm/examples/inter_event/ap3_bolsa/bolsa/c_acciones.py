# -*- encoding: utf-8 -*-
""" GAcciones GObj

.. autoclass:: GAcciones
    :members: start_up

"""

from ginsfsm.gobj import GObj


def ac_acciones(self, event):
    """ Event attributes:
        * :attr:`acciones`: .

    """
    acciones = int(event.acciones)
    user_name = event.user_name
    if not user_name in self.user_acciones:
        self.user_acciones[user_name] = acciones
    else:
        self.user_acciones[user_name] += acciones

    if event.__intra_event__:
        origin_gaplic = event.__intra_event__.origin_gaplic
        origin_role = event.__intra_event__.origin_role
        origin_gobj = event.__intra_event__.origin_gobj

        self.gaplic.send_event_outside(
            origin_gaplic,  # gaplic_name
            origin_role,  # role
            origin_gobj,  # gobj_name
            'EV_ACCIONES_ACK',  # event_name
            self,  # subscriber_gobj
            acciones=self.user_acciones[user_name],
        )


ACCIONES_FSM = {
    'event_list': (
        'EV_ACCIONES:top input',
        'EV_ACCIONES_ACK:top output',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_ACCIONES',      ac_acciones,      None),
        ),
    }
}

ACCIONES_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class GAcciones(GObj):
    """  GAcciones GObj.
    A Sample gobj.

    .. ginsfsm::
       :fsm: ACCIONES_FSM
       :gconfig: ACCIONES_GCONFIG

    *Input-Events:*
        * :attr:`'EV_ACCIONES'`: sample input event.

          Event attributes:

              * ``data``: sample event attribute.

    *Output-Events:*
        * :attr:`'EV_ACCIONES_ACK'`: sample output event.

          Event attributes:

              * ``data``: sample event attribute.

    """
    def __init__(self):
        GObj.__init__(self, ACCIONES_FSM, ACCIONES_GCONFIG)
        self.user_acciones = {}

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.subscriber:
            self.subscribe_event(None, self.config.subscriber)
