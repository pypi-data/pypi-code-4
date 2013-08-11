# coding=utf-8
from __future__ import unicode_literals

"""
Utility library for interacting with unimate
"""
import socket
import types


class Client(object):
    """
    Unimate client
    """
    def __init__(self, server, port):
        if not isinstance(server, types.StringTypes):
            raise TypeError("server must be a string")
        if not isinstance(port, (int, long)):
            raise TypeError("port must be an integer")
        self._server = server
        self._port = port

    def send(self, message, room=None):
        """Broadcast a message through unimate"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._server, self._port))
 
        if isinstance(message, str):
            message = message.decode('utf-8')

        if room is None:
            msg = "broadcast %s\r\n" % message
        else:
            if isinstance(room, str):
                room = room.decode('utf-8')
            msg = "broadcast %s %s\r\n" % (room, message)

        assert isinstance(msg, unicode)
        msg = msg.encode('utf-8')

        sock.send(msg)
        sock.close()

class DummyUnimate(object):
    def send(self, message, room = None):
        pass

if __name__ == '__main__':
    Client("unimate.corp.smarkets.com", 12344).send(u"Tëßt")
