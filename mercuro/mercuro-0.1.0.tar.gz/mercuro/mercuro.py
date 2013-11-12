# -*- encoding: utf-8 -*-
#
# Copyright © 2013 SoftLayer Technologies, an IBM company
#
# Author: Brian Cline <bcline@softlayer.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function
from SocketServer import UDPServer, BaseRequestHandler
import time
import bernhard


DEFAULT_TRANSPORT = 'tcp'


class MercuroUDPServer():
    def __init__(self, listen_host='0.0.0.0', listen_port=2554,
                 riemann_host='127.0.0.1', riemann_port=5555,
                 riemann_transport=DEFAULT_TRANSPORT):
        handler_type = transport_name_to_transport(riemann_transport)
        self.server = UDPServer((self.listen_host, self.listen_port),
                                handler_type)

        self.riemann = bernhard.Client()

    def serve(self):
        self.server.serve_forever()


class RequestHandler(BaseRequestHandler):
    def handle(self):
        if not self.riemann.client:
            self.riemann = bernhard.Client()

        data = self.request[0].strip()
        event = {'time': time.time(),
                 'description': data}
        self.riemann.write(event)

        print("%s wrote %d bytes:" % (self.client_address[0],
                                      len(data)))
        print("%s" % data)


transports = {
    'tcp': RequestHandler,
    'udp': RequestHandler
}


def transport_name_to_transport(transport_name):
    if transport_name not in transports:
        return transports[DEFAULT_TRANSPORT]

    return transports[transport_name]
