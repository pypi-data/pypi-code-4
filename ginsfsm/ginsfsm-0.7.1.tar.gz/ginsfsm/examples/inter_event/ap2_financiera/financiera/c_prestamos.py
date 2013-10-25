# -*- encoding: utf-8 -*-
""" GPrestamos GObj

.. autoclass:: GPrestamos
    :members: start_up

"""

from ginsfsm.gobj import GObj


def ac_prestamo(self, event):
    """ Event attributes:
        * :attr:`euros`: .

    """
    euros = int(event.euros)
    user_name = event.user_name
    if not user_name in self.user_prestamos:
        self.user_prestamos[user_name] = euros
    else:
        self.user_prestamos[user_name] += euros

    if event.__intra_event__:
        origin_gaplic = event.__intra_event__.origin_gaplic
        origin_role = event.__intra_event__.origin_role
        origin_gobj = event.__intra_event__.origin_gobj

        self.gaplic.send_event_outside(
            origin_gaplic,  # gaplic_name
            origin_role,  # role
            origin_gobj,  # gobj_name
            'EV_PRESTAMO_ACK',  # event_name
            self,  # subscriber_gobj
            euros=self.user_prestamos[user_name],
        )


PRESTAMOS_FSM = {
    'event_list': (
        'EV_PRESTAMO:top input',
        'EV_PRESTAMO_ACK:top output',
    ),
    'state_list': (
        'ST_IDLE',
    ),
    'machine': {
        'ST_IDLE':
        (
            ('EV_PRESTAMO',      ac_prestamo,      None),
        ),
    }
}

PRESTAMOS_GCONFIG = {
    'subscriber': [
        None, None, 0, None,
        "subcriber of all output-events."
        "Default is ``None``, i.e., the parent"
    ],
}


class GPrestamos(GObj):
    """  GPrestamos GObj.
    A Sample gobj.

    .. ginsfsm::
       :fsm: PRESTAMOS_FSM
       :gconfig: PRESTAMOS_GCONFIG

    *Input-Events:*
        * :attr:`'EV_PRESTAMO'`: sample input event.

          Event attributes:

              * ``data``: sample event attribute.

    *Output-Events:*
        * :attr:`'EV_PRESTAMO_ACK'`: sample output event.

          Event attributes:

              * ``data``: sample event attribute.

    """
    def __init__(self):
        GObj.__init__(self, PRESTAMOS_FSM, PRESTAMOS_GCONFIG)
        self.user_prestamos = {}

    def start_up(self):
        """ Initialization zone.
        """
        if self.config.subscriber:
            self.subscribe_event(None, self.config.subscriber)
