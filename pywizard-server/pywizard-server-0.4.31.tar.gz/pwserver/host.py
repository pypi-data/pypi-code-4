import json
from logging import debug, info
import os
import pywizard
from pywizard.utils.file_transfer import create_transfer_package, load_package_from_fs


class PywizardHost():
    upstream = None
    downstream = None

    name = None
    pywizard_server = None

    # def connect(self, port, socket):
    #         ssh.tunnel_connection(
    #             socket,
    #             'tcp://%s:%s' % (config['tunnel']['host'], port),
    #             config['tunnel']['via'],
    #             paramiko=True,
    #             password=config['tunnel']['password']
    #         )

    def __init__(self, pywizard_server, name):

        self.pywizard_server = pywizard_server
        self.name = name

        # if 'tunnel' in config:
        #     req = pywizard_server.zmq_context.socket(zmq.PUB)
        #     self.connect(config, 7375, req)
        #
        #     self.upstream = zmqstream.ZMQStream(req)
        #
        #     socket = pywizard_server.zmq_context.socket(zmq.SUB)
        #     self.connect(7373, socket)
        #     socket.setsockopt(zmq.SUBSCRIBE, "")
        #     self.downstream = zmqstream.ZMQStream(socket)
        #     self.downstream.on_recv(self.on_message)

    def send_websocket_message(self, message):
        self.pywizard_server.send_websocket_message({
            'host': self.name,
            'msg': message,
        })

    def on_message(self, messages):
        message = messages[-1]
        self.send_websocket_message(json.loads(message))

    def get_config(self):
        return self.pywizard_server.config_source.get_node_config(self.name)

    def get_upstream(self):
        return self.upstream or self.pywizard_server.upstream

    def get_context(self):
        return self.get_config()['context']

    def get_others_context(self):
        return [
            self.pywizard_server.get_host(host).get_context()

            for host in self.pywizard_server.config_source.get_node_group_hosts(self.name)
        ]

    def ws_log(self, msg):
        self.send_websocket_message({'cmd': 'log', 'data': msg})

    def on_websocket_message(self, message):

        debug(message)

        config = self.get_config()

        if message['cmd'] == 'provision':

            package_ = config['me']['package']
            if not package_:
                self.ws_log('You have no provisioning packages uploaded yet.')
                return

            with open(package_) as f:
                pkgs = json.load(f)

            pywizard_pkg = pkgs['pywizard']
            provision_pkg = pkgs['provision']

            self.get_upstream().send_multipart([self.name, json.dumps({
                'cmd': 'pywizard_pkg',
                'data': {
                    'pkg': pywizard_pkg,
                }
            })])

            self.get_upstream().send_multipart([self.name, json.dumps({
                'cmd': 'provision_pkg',
                'data': {
                    'path': config['me']['path'],
                    'pkg': provision_pkg,
                }
            })])

            self.get_upstream().send_multipart([self.name, json.dumps({
                'cmd': 'provision',
                'data': {
                    'context': config,
                    'script': config['me']['script'],
                    'path': config['me']['path'],
                    'log-level': config['me']['log-level'],
                    'roles': config['me']['roles'],
                }
            })])
            return

        else:
            message['data'] = message['cmd']
            message['cmd'] = 'shell'

        self.get_upstream().send_multipart([self.name, json.dumps(message)])
