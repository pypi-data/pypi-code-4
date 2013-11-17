#!/usr/bin/env python
# -*- coding: utf8 -*-
from twisted.internet.protocol import Factory, Protocol
import hashlib, struct, base64
import threading, time

class WSHandler(Protocol):
    """WebSocket handler Protocol"""

    def __init__(self, sockets):
        self.sockets = sockets

    def connectionMade(self):
        if not self.sockets.has_key(self):
            self.sockets[self] = {}

    def connectionLost(self, reason):
        if self.sockets.has_key(self):
            del self.sockets[self]

    def dataReceived(self, msg):
        if msg.lower().find('upgrade: websocket') != -1:
            self._hand_shake(msg)
        else:
            raw_str = self._parse_recv_data(msg)
            self.onMessage(raw_str)

    def onMessage(self, msg):
        """receive message from ws client"""
        # send back like echo
        self.send(msg)

    def send(self, msg):
        """Send message to ws client"""
        if self.sockets[self]['new_version']:
            # hybi-10
            op = 0x80 | (0x01 & 0x0f)  # 0x81
            data_length = len(msg)

            if data_length <= 125:
                header = struct.pack(">BB", op, data_length)
            elif data_length <= 65535:
                header = struct.pack(">BBH", op, 126, data_length)
            else:
                header = struct.pack(">BBQ", op, 127, data_length)
            text = header + msg
        else:
            # hixie-76
            text = '\x00%s\xFF' % msg

        self.transport.write(text)


    def _generate_token(self, key1, key2, key3):
        num1 = int("".join([digit for digit in list(key1) if digit.isdigit()]))
        spaces1 = len([char for char in list(key1) if char == " "])
        num2 = int("".join([digit for digit in list(key2) if digit.isdigit()]))
        spaces2 = len([char for char in list(key2) if char == " "])

        combined = struct.pack(">II", num1/spaces1, num2/spaces2) + key3
        return hashlib.md5(combined).digest()

    def _generate_token_2(self, key):
        key = key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        ser_key = hashlib.sha1(key).digest()
        return base64.b64encode(ser_key)

    def _parse_recv_data(self, msg):
        raw_str = ''

        if self.sockets[self]['new_version']:
            code_length = ord(msg[1]) & 127

            if code_length == 126:
                masks = msg[4:8]
                data = msg[8:]
            elif code_length == 127:
                masks = msg[10:14]
                data = msg[14:]
            else:
                masks = msg[2:6]
                data = msg[6:]

            i = 0
            for d in data:
                raw_str += chr(ord(d) ^ ord(masks[i%4]))
                i += 1
        else:
            raw_str = msg.split("\xFF")[0][1:]

        return raw_str

    def _hand_shake(self, msg):
        """WebSocket handshake"""
        headers = {}
        header, data = msg.split('\r\n\r\n', 1)
        for line in header.split('\r\n')[1:]:
            key, value = line.split(": ", 1)
            headers[key] = value

        headers["Location"] = "ws://%s/" % headers["Host"]

        if headers.has_key('Sec-WebSocket-Key1'):
            key1 = headers["Sec-WebSocket-Key1"]
            key2 = headers["Sec-WebSocket-Key2"]
            key3 = data[:8]

            token = self._generate_token(key1, key2, key3)

            handshake = '\
HTTP/1.1 101 Web Socket Protocol Handshake\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Origin: %s\r\n\
Sec-WebSocket-Location: %s\r\n\r\n\
' %(headers['Origin'], headers['Location'])

            self.transport.write(handshake + token)
            self.sockets[self]['new_version'] = False
        else:
            key = headers['Sec-WebSocket-Key']
            token = self._generate_token_2(key)

            handshake = '\
HTTP/1.1 101 Switching Protocols\r\n\
Upgrade: WebSocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Accept: %s\r\n\r\n\
' % (token)
            self.transport.write(handshake)
            self.sockets[self]['new_version'] = True


class WSHandlerFactory(Factory):
    def __init__(self, hclass=None):
        if hclass==None:
            self._handler_class = WSHandler
        else:
            assert issubclass(hclass, WSHandler)
            self._handler_class = hclass

        self.sockets = {}

    def buildProtocol(self, addr):
        return self._handler_class(self.sockets)


if __name__=="__main__":
    from twisted.internet import reactor
    reactor.listenTCP(1337, WSHandlerFactory())
    reactor.run()

