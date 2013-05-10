# -*- encoding: utf-8 -*-
""" Cuentas GObj

.. autoclass:: Cuentas
    :members: start_up

"""

from ginsfsm.gobj import GObj


def ac_cuenta(self, event):
    """ Event attributes:
        * :attr:`user_name`: user name.

    """
    user_name = event.user_name
    if not user_name in self.cuentas:
        self.cuentas[user_name] = 0

    if event.__intra_event__:
        origin_gaplic = event.__intra_event__.origin_gaplic
        origin_role = event.__intra_event__.origin_role
        origin_gobj = event.__intra_event__.origin_gobj

        self.gaplic.send_event_outside(
            origin_gaplic,  # gaplic_name
            origin_role,  # role
            origin_gobj,  # gobj_name
            'EV_CUENTA_ACK',  # event_name
            self,  # subscriber_gobj
        )


CUENTAS_FSM = {
    'event_list': (
        'EV_CUENTA:top input',
        'EV_CUENTA_ACK:top output',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_CUENTA',      ac_cuenta,      None),
        ),
    }
}

CUENTAS_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class Cuentas(GObj):
    """  Cuentas GObj.
    A Sample gobj.

    .. ginsfsm::
       :fsm: CUENTAS_FSM
       :gconfig: CUENTAS_GCONFIG

    *Input-Events:*
        * :attr:`'EV_CUENTA'`: sample input event.

          Event attributes:

              * ``data``: sample event attribute.

    *Output-Events:*
        * :attr:`'EV_CUENTA_ACK'`: sample output event.

          Event attributes:

              * ``data``: sample event attribute.

    """
    def __init__(self):
        GObj.__init__(self, CUENTAS_FSM, CUENTAS_GCONFIG)
        self.cuentas = {}

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.subscriber:
            self.subscribe_event(None, self.config.subscriber)
