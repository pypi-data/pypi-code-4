""" neehi.cm - context managers for neehi

This module provides context managers to quickly force third-party
libraries, which use sockets, to direct their traffic through
a proxy.

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
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import socket

import neehi


class ProxyContextManager(object):
    """ Base class for proxy context managers.
    """
    def __enter__(self):
        self._orgsocket = socket.socket
        socket.socket = neehi.socksocket
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        socket.socket = self._orgsocket
        return False


class SocksProxy5(ProxyContextManager):
    """ Direct all newly opened socket traffic through the designated
        SOCKS5 proxy.

        >>> import urllib
        >>> import neehi
        >>> from neehi.cm import SocksProxy5
        >>> with SocksProxy5('127.0.0.1'):
        ...     try:
        ...         urllib.urlopen("http://www.example.com")
        ...     except neehi.ProxyError as e:
        ...         print(e)
        >>>
    """
    def __init__(self, addr, port=1080, rdns=True, username=None,
                    password=None):
        neehi.setdefaultproxy(neehi.PROXY_TYPE_SOCKS5, addr, port, rdns,
                                username, password)


class SocksProxy4(ProxyContextManager):
    """ Direct all newly opened socket traffic through the designated
        SOCKS4 proxy.

        >>> import urllib
        >>> import neehi
        >>> from neehi.cm import SocksProxy4
        >>> with SocksProxy4('127.0.0.1'):
        ...     try:
        ...         urllib.urlopen("http://www.example.com")
        ...     except neehi.ProxyError as e:
        ...         print(e)
        >>>
    """
    def __init__(self, addr, port=1080, rdns=True, username=None):
        neehi.setdefaultproxy(neehi.PROXY_TYPE_SOCKS4, addr, port, rdns,
                                username)


class HttpProxy(ProxyContextManager):
    """ Direct all newly opened socket traffic through the designated
        HTTP CONNECT proxy.

        >>> import urllib
        >>> import neehi
        >>> from neehi.cm import HttpProxy
        >>> with HttpProxy('127.0.0.1'):
        ...     try:
        ...         urllib.urlopen("http://www.example.com")
        ...     except neehi.ProxyError as e:
        ...         print(e)
        >>>
    """
    def __init__(self, addr, port=8080, rdns=True):
        neehi.setdefaultproxy(neehi.PROXY_TYPE_HTTP, addr, port, rdns)

