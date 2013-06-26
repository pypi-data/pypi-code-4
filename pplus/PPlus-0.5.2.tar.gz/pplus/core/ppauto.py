"""Parallel Python Software, Auto-Discovery Service"""

# Author: Vitalii Vanovschi <support@parallelpython.com>,
#         Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Grzegorz Zycinski <grzegorz.zycinski@disi.unige.it>
# License: new BSD.

import socket
import sys
import time

from . import ppcommon

# broadcast every 10 sec
BROADCAST_INTERVAL = 10

class Discover(object):
    """Auto-discovery service class"""

    def __init__(self, base, isclient=False):
        self.base = base
        self.hosts = []
        self.isclient = isclient

    def run(self, interface_addr, broadcast_addr):
        """Starts auto-discovery"""
        self.interface_addr = interface_addr
        self.broadcast_addr = broadcast_addr
        self.bsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bsocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            self.listen()
        except:
            sys.excepthook(*sys.exc_info())

    def broadcast(self):
        """Sends a broadcast"""
        if self.isclient:
            self.base.logger.debug("Client sends initial broadcast to (%s, %i)"
                    % self.broadcast_addr)
            self.bsocket.sendto("C", self.broadcast_addr)
        else:
            while True:
                if self.base._exiting:
                    return
                self.base.logger.debug("Server sends broadcast to (%s, %i)"
                        % self.broadcast_addr)
                self.bsocket.sendto("S", self.broadcast_addr)
                time.sleep(BROADCAST_INTERVAL)


    def listen(self):
        """Listens for broadcasts from other clients/servers"""
        self.base.logger.debug("Listening (%s, %i)" % self.interface_addr)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.settimeout(5)
        self.socket.bind(self.interface_addr)

        ppcommon.start_thread("broadcast",  self.broadcast)

        while True:
            try:
                if self.base._exiting:
                    return
                message, (host, port) = self.socket.recvfrom(1024)
                remote_address = (host, self.broadcast_addr[1])
                hostid = host + ":" + str(self.broadcast_addr[1])
                self.base.logger.debug("Discovered host (%s, %i) message=%c"
                        % (remote_address + (message[0], )))
                if not self.base.autopp_list.get(hostid, 0) and self.isclient \
                        and message[0] == 'S':
                    self.base.logger.debug("Connecting to host %s" % (hostid, ))
                    ppcommon.start_thread("ppauto_connect1",  self.base.connect1,
                            remote_address+(False, ))
                if not self.isclient and message[0] == 'C':
                    self.base.logger.debug("Replying to host %s" % (hostid, ))
                    self.bsocket.sendto("S", self.broadcast_addr)
            except socket.timeout:
                pass
            except:
                self.base.logger.error("An error has occured during execution of "
                        "Discover.listen")
                sys.excepthook(*sys.exc_info())
