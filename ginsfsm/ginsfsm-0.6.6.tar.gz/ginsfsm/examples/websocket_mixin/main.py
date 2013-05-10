import logging
logging.basicConfig(level=logging.DEBUG)

from ginsfsm.gobj import GObj
from ginsfsm.c_connex import GConnex
from ginsfsm.gaplic import GAplic, setup_gaplic_thread
from ginsfsm.c_timer import GTimer
from ginsfsm.c_srv_sock import GServerSock


#===============================================================
#   Server: emit a message to clients each 5 seconds
#===============================================================
def ac_clisrv_timeout(self, event):
    self.set_timeout(5)
    for child in self.clients:
        self.send_event(child, 'EV_SEND_DATA', data='xxxxxx')


def ac_clisrv_connected(self, event):
    self.clients.add(event.gsock)


def ac_clisrv_disconnected(self, event):
    self.clients.remove(event.gsock)
    self.destroy_gobj(event.source[-1])


def ac_clisrv_rx_data(self, event):
    # Do echo
    self.send_event(event.source[-1], 'EV_SEND_DATA', data=event.data)


SERVER_FSM = {
    'event_list': (
        'EV_SET_TIMER: bottom output',
        'EV_TIMEOUT: bottom input',
        'EV_CONNECTED: bottom input',
        'EV_DISCONNECTED: bottom input',
        'EV_RX_DATA:bottom input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_TIMEOUT',          ac_clisrv_timeout,         'ST_IDLE'),
            ('EV_CONNECTED',        ac_clisrv_connected,       'ST_IDLE'),
            ('EV_DISCONNECTED',     ac_clisrv_disconnected,    'ST_IDLE'),
            ('EV_RX_DATA',          ac_clisrv_rx_data,         'ST_IDLE'),
        ),
    }
}


SERVER_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'verbose': [int, 1, 0, None, "Increase output verbosity. Values [0,1,2]"],
}


class OnServer(GObj):
    """  Server GObj.

    .. ginsfsm::
       :fsm: SERVER_FSM
       :gconfig: SERVER_GCONFIG

    *Input-Events:*

        * :attr:`'EV_TIMEOUT'`: Timer over.
            Start the machine.

        * :attr:`'EV_CONNECTED'`: New client.

        * :attr:`'EV_DISCONNECTED'`: Client disconnected.

        * :attr:`'EV_RX_DATA'`: Receiving data.

    *Output-Events:*

    """
    def __init__(self):
        GObj.__init__(self, SERVER_FSM, SERVER_GCONFIG)
        self.clients = set()

    def start_up(self):
        self.timer = self.create_gobj(
            None,
            GTimer,
            self)
        self.set_timeout(5)

        self.server = self.create_gobj(
            None,
            GServerSock,
            self,
            host='0.0.0.0',
            port=10000,
            transmit_ready_event_name=None,
        )

    def set_timeout(self, seconds):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=seconds)

    def clear_timeout(self):
        self.send_event(self.timer, 'EV_SET_TIMER', seconds=-1)


#===============================================================
#                   Driver
#===============================================================
def ac_rx_data(self, event):
    data = event.kw['data']
    print("RECIBO======> %s" % data)
    self.broadcast_event('EV_UPDATE_DRIVER', data=data)


def ac_comando(self, event):
    self.broadcast_event('EV_UPDATE_DRIVER', data='QUE SIIIIIIIIII')


DRIVER1_FSM = {
    'event_list': (
        'EV_UPDATE_DRIVER:top output',
        'EV_RX_DATA:bottom input',
        'EV_COMANDO: top input',
    ),
    'state_list': ('ST_IDLE',),
    'machine': {
        'ST_IDLE':
        (
            ('EV_RX_DATA',      ac_rx_data,     'ST_IDLE'),
            ('EV_COMANDO',      ac_comando,     'ST_IDLE'),
        ),
    }
}


DRIVER1_GCONFIG = {  # type, default_value, flag, validate_function, desc
    'host': [str, 'localhost', 0, None, ""],
    'port': [int, 10000, 0, None, ""],
}


class Driver1(GObj):
    """  Driver1 GObj.

    .. ginsfsm::
       :fsm: DRIVER1_FSM
       :gconfig: DRIVER1_GCONFIG

    *Input-Events:*

        * :attr:`'EV_RX_DATA'`: Receiving data.
            Receiving data from urls.

    *Output-Events:*

    """
    def __init__(self):
        GObj.__init__(self, DRIVER1_FSM, DRIVER1_GCONFIG)

    def start_up(self):
        """ Initialization zone."""
        self.timer = self.create_gobj(
            None,
            GTimer,
            self,
        )
        self.connex = self.create_gobj(
            'connex',
            GConnex,
            self,
            destinations=[
                (self.config.host, self.config.port),
            ],
            #host=self.config.host,
            #port=self.config.port,
            # only want receive EV_RX_DATA event
            connected_event_name=None,
            disconnected_event_name=None,
            transmit_ready_event_name=None,
        )


#===============================================================
#                   Main
#===============================================================
def mycallback(event):
    print("CALLBACK recibiendo %s" % event.data)

if __name__ == "__main__":
    local_conf = {
        'GObj.trace_mach': True,
        'GObj.logger': logging,
    }

    #---------------------------------------------#
    #
    #---------------------------------------------#
    ga_srv = GAplic(name='server', roles='', **local_conf)
    ga_srv.create_gobj(
        'server',
        OnServer,
        ga_srv,
    )
    thread_server = setup_gaplic_thread(ga_srv)
    thread_server.start()

    #---------------------------------------------#
    #
    #---------------------------------------------#
    local_conf = {
        'router_enabled':  True,
        'GRouter.server':  True,
        'GRouter.localhost_route_ports':  8002,
        'GRouter.trace_router':  True,
        'GObj.trace_mach':  True,
        'GObj.trace_creation':  False,
        'GObj.trace_traverse':  True,
        'GObj.trace_subscription':  False,
        'GSock.trace_dump':  True,
        'GObj.logger': logging,
    }
    ga_driver = GAplic(name='Protocolo1', roles='domotica', **local_conf)
    ga_driver.create_gobj(
        'driver',
        Driver1,
        ga_driver,
        __unique_name__=True,
    )
    thread_driver = setup_gaplic_thread(ga_driver)
    thread_driver.start()

    #---------------------------------------------#
    #   Code to insert in a non-gobj code.
    #       Subscribe as callback
    #---------------------------------------------#
    from ginsfsm.globals import global_get_gobj
    from ginsfsm.deferred import Deferred

    defer = Deferred(0, mycallback)
    gobj = global_get_gobj('driver')
    if gobj:
        gobj.subscribe_event('EV_UPDATE_DRIVER', defer)

    #---------------------------------------------#
    #       Loop
    #---------------------------------------------#
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        print('Program stopped')

    thread_server.stop()
    thread_driver.stop()
    thread_server.join()
    thread_driver.join()
