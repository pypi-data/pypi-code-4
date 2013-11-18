#!/usr/bin/env python

'''
Socket module
'''

import socket


class connection(object):
    '''
    Socket connection class
    '''

    '''Socket resource'''
    _res = None
    _timeout = 0.5

    def __init__(self, hostname='', port=0, timeout=5, blocking=1):
        '''
        Socket connection constructor
            :param str hostname: Hostname or IP address of Axigen server
            :param int port: Port of the Axigen CLI service
            :param float timeout: Timeout in seconds for connecting to
                Axigen CLI
            :param int blocking: Make the socket connection blocking
        '''
        sock = None
        family = 'anything'
        if (hostname != '' and port > 0):
            # Attempt to connect in all (IPv4/v6) ways until one is
            # successful or until one connection method doesn't work
            # anymore.
            while ((sock is None) and (family is not None)):
                try:
                    res = list(socket.getaddrinfo(
                        hostname, port, 0, 0, socket.SOL_TCP
                    ))
                    pres = res.pop()
                    self._timeout = timeout
                except (socket.gaierror, socket.herror), message:
                    raise SocketError(message)
                if (pres is not None):
                    family, socktype, proto, canonname, sockaddr = pres
                    try:
                        sock = socket.socket(family, socktype, proto)
                        sock.setblocking(blocking)
                        sock.settimeout(timeout)
                    except socket.error, message:
                        sock = None
                        raise SocketError(message)
                    try:
                        sock.connect(sockaddr)
                    except socket.error, message:
                        sock.close()
                        sock = None
                        raise ConnectionError(message)
            self._res = sock

    def __del__(self):
        '''
        Socket connection destructor
        '''
        if (self._res is not None):
            self._res.close()

    def _receive(self, size=1024):
        '''
        Internal receive method
            :param int size: Size of the "frame"
            :return: str
        '''
        self._res.settimeout(0.5)
        data = ''
        if (self._res is not None):
            try:
                recv = self._res.recv(size)
                while (len(recv)):
                    data += recv
                    recv = self._res.recv(size)
            except socket.error:
                recv = False
        self._res.settimeout(self._timeout)
        return(data)

    def _receive_once(self, size=1024):
        '''
        Internal "shot_receive" method
            :param int size: Size of the "frame"
            :return: str
        '''
        try:
            recv = self._res.recv(size)
        except socket.error:
            recv = False
        return(recv)

    def _send(self, data=''):
        '''
        Internal send method
            :param str data: Data to be sent
            :return: bool
        '''
        status = False
        if (self._res is not None):
            status = True
            try:
                self._res.sendall(data)
            except socket.error:
                status = False
        return(status)


class ConnectionError(Exception):
    '''
    connection.ConnectionError exception
    for problems with socket connection
    '''


class SocketError(Exception):
    '''
    connection.SocketError exception
    for various pre-connection socket errros
    '''
