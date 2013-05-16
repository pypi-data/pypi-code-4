""" Mocked classes/objects for testing the neehi module.

Copyright 2012 Sean Robinson <seankrobinson@gmail.com>

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the author nor the names of contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMANGE.
"""

from collections import deque


def gethostbyname(address):
    """ Mock socket.gethostbyname to return the same address for every
        query.
    """
    return lambda x: address


class MockSocket(object):
    """ Mock of a socket.socket with internal FIFOs from which
        consumers may recv() messages or to which producers may
        send messages.  The two FIFOs are separate to reduce
        confusion about objects stored on each.
    """
    def __init__(self, family, type_, proto, sock):
        """ Create a MockSocket.  family, type_, proto, and sock are
            ignored.
        """
        self._address = None
        self._destination = None
        self._recv_deque = deque()
        self._send_deque = deque()

    def load_recv_deque(self, iterable):
        """ Put iterables items into recv FIFO for later receiving.
        """
        for item in iterable:
            if not isinstance(item, bytes):
                raise ValueError('Because MockSocket simulates a socket,' +
                    ' all values to be returned by it must be bytes.' +
                    ' No str allowed.')
            self._recv_deque.append(item)

    def set_address(self, address):
        """ Set the address value to be returned by getpeername().
            address must be a tuple of (address, port).
        """
        if not isinstance(address, tuple):
            raise ValueError('address must be a tuple of the AF_INET address')
        self._address = address

    def connect(self, destination):
        """ Pretend to connect to destination, but, really, save it for
            later inspection.
        """
        self._destination = destination

    def sendall(self, message):
        """ Pretend to send a message, instead, save it.
        """
        self._send_deque.append(message)

    def send(self, message):
        """ Pretend to send a message, instead, save it.
        """
        self._send_deque.append(message)

    def recv(self, bufsize, flags=None):
        """ Return the saved message.
        """
        return self._recv_deque.popleft()

    def getpeername(self):
        """ Return the
        """
        return self._address

    def close(self):
        """ Fake the closing of the socket.
        """
        pass

