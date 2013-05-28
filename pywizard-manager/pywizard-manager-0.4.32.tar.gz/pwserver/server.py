import json
from logging import warn, info
from tornado import websocket
import zmq
from zmq.eventloop import zmqstream
from pwserver.config import ConfigSource
from pwserver.host import PywizardHost


class WebSocketHandler(websocket.WebSocketHandler):

    pywizard_server = None

    def initialize(self, pywizard_server=None):
        super(WebSocketHandler, self).initialize()
        self.pywizard_server = pywizard_server

    def open(self):
        self.pywizard_server.opened_websocket_connections.append(self)

    def on_message(self, message):
        message = json.loads(message)
        if message['host'] in self.pywizard_server.hosts:
            host = self.pywizard_server.hosts[message['host']]
            host.on_websocket_message(message['msg'])

    def on_close(self):
        self.pywizard_server.opened_websocket_connections.remove(self)


class PywizardServer():

    config_source = None
    zmq_context = None
    opened_websocket_connections = None
    hosts = None
    upstream = None
    downstream = None

    def bind_sockets(self, bind_host='127.0.0.1', in_port=7373, out_port=7375):

        req = self.zmq_context.socket(zmq.PUB)
        req.bind('tcp://%s:%s' % (bind_host, out_port))
        self.upstream = zmqstream.ZMQStream(req)

        info('Zmq OUT socket started at %s:%d' % (bind_host, out_port))

        socket = self.zmq_context.socket(zmq.SUB)
        socket.bind('tcp://%s:%s' % (bind_host, in_port))
        socket.setsockopt(zmq.SUBSCRIBE, "")
        self.downstream = zmqstream.ZMQStream(socket)
        self.downstream.on_recv(self.on_message)

        info('Zmq IN socket started at %s:%d' % (bind_host, in_port))

    def __init__(self, config_source):

        if not isinstance(config_source, ConfigSource):
            raise Exception('Config source has not valid type: %s' % type(config_source))

        self.zmq_context = zmq.Context()
        self.hosts = {}
        self.config_source = config_source
        self.opened_websocket_connections = []

    def on_message(self, message):
        print message
        host = message[0]
        if '.' in host:
            host = host.split('.')[0]

        known_hosts = self.config_source.get_node_list()

        if not host in known_hosts:
            warn('Unknown host tried to connect: %s' % host)
            return

        self.get_host(host).on_message(message)

    def get_host(self, name):
        if not name in self.hosts:
            self.add_host(name)

        return self.hosts[name]

    def add_host(self, name):
        host = PywizardHost(self, name)
        self.hosts[name] = host

    def send_websocket_message(self, message):
        for con in self.opened_websocket_connections:
            con.write_message(message)

