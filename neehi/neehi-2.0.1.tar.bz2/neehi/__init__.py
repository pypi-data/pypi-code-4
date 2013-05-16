""" neehi - a Python SOCKS/HTTP proxy module

Version 2.0.1

This module provides a standard socket-like interface for Python
developers to tunnel connections through SOCKS4, SOCKS5, and
HTTP CONNECT proxies.

Copyright 2006 Dan-Haim. All rights reserved.
Copyright 2012 Yann <asterix@lagaule.org>
Copyright 2012 Mario Vilas
Copyright 2012 Robin Macharg
Copyright 2012 Sean Robinson <seankrobinson@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of Dan Haim nor the names of his contributors may
   be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY DAN HAIM "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN
NO EVENT SHALL DAN HAIM OR HIS CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMANGE.
"""

import socket
import struct

PROXY_TYPE_SOCKS4 = 1
PROXY_TYPE_SOCKS5 = 2
PROXY_TYPE_HTTP = 3

_defaultproxy = None
_orgsocket = socket.socket


class GeneralResult(object):
    SUCCESS = 0
    EINVALID = 1
    ENOTCONN = 2
    ENOTAVAIL = 3
    EBADPROXYTYPE = 4
    EBADINPUT = 5

    MSG = ("Success", "Invalid data", "Not connected",
           "Not available", "Bad proxy type", "Bad input")

class Socks5Result(object):
    SUCCESS = 0
    FAILGEN = 1
    ENOTALLOWED = 2
    ENETUNREACH = 3
    EHOSTUNREACH = 4
    ECONNREFUSED = 5
    TTLEXPIRED = 6
    ENOTSUP = 7
    EAFNOSUPPORT = 8
    UNKNOWN = 9

    MSG = ("Success", "General SOCKS server failure",
           "Connection not allowed by ruleset", "Network unreachable",
           "Host unreachable", "Connection refused",
           "TTL expired", "Command not supported",
           "Address type not supported", "Unknown error")

class Socks5AuthResult(object):
    SUCCESS = 0
    AUTHREQ = 1
    EAUTHREJ = 2
    EAUTHFAIL = 3
    UNKNOWN = 4

    MSG = ("Success", "Authentication required",
           "All offered authentication methods were rejected",
           "Unknown username or invalid password", "Unknown error")

class Socks4Result(object):
    OFFSET = 90

    SUCCESS = 0
    EREJECT = 1
    EIDCONN = 2
    EIDDIFF = 3
    UNKNOWN = 4

    MSG = ("Request granted", "Request rejected or failed",
           "Request rejected, SOCKS server cannot connect to client's identd",
           "Request rejected, different user reported",
           "Unknown error")


class ProxyError(Exception):
    """ Base exception class for socksocket errors. """
    def __str__(self):
        return '%s' % ' '.join(map(str, self.args))


class GeneralProxyError(ProxyError):
    """ Errors of a general nature with the proxy (e.g. invalid data,
        cannot connect).

        Possible sources for these exceptions include:

        GeneralResult.EINVALID - Invalid data - This error means that
        unexpected data has been received from the server.  The most
        common reason is that the server specified as the proxy is not
        really a SOCKS4/SOCKS5/HTTP proxy, or maybe the proxy type
        specified is wrong.

        GeneralResult.EBADPROXYTYPE - Bad proxy type - This will be
        raised if the type of the proxy supplied to the setproxy method
        was not one of PROXY_TYPE_SOCKS4, PROXY_TYPE_SOCKS5, or
        PROXY_TYPE_HTTP.

        GeneralResult.EBADINPUT - Bad input - This will be raised if
        the connect method is called with bad input parameters.
    """
    def __str__(self):
        return '[%s] %s' % (self.args[0], GeneralResult.MSG[self.args[0]])


class Socks5Error(ProxyError):
    """ Errors specific to the SOCKS5 proxy (e.g. connection not allowed,
        network or host unreachable).

        Possible sources for these exceptions include:

        Socks5Result.FAILGEN - General SOCKS5 server failure - If, for
        any reason, the proxy server is unable to fulfill your request
        (internal server error).

        Socks5Result.ENOTALLOWED - Connection not allowed by ruleset - If
        the address you're trying to connect to is blacklisted on the
        server or requires authentication.

        Socks5Result.ENETUNREACH - Network unreachable - The target could
        not be contacted. A router on the network has replied with a
        "destination net unreachable" error.

        Socks5Result.EHOSTUNREACH - Host unreachable - The target could
        not be contacted. A router on the network has replied with a
        "destination host unreachable" error.

        Socks5Result.ECONNREFUSED - Connection refused - The target
        has refused the connection (the requested port is closed).

        Socks5Result.TTLEXPIRED - TTL expired - The TTL value of the SYN
        packet from the proxy to the target has expired. This usually
        means that there are network problems causing the packet to be
        caught in a router-to-router "ping-pong".

        Socks5Result.ENOTSUP - Command not supported - The client has
        issued an invalid command.  When using this package, this error
        should not occur.

        Socks5Result.EAFNOSUPPORT - Address type not supported - The
        client has provided an invalid address type.  When using this
        package, this error should not occur.
    """
    def __str__(self):
        return '[%s] %s' % (self.args[0], Socks5Result.MSG[self.args[0]])


class Socks5AuthError(Socks5Error):
    """ Errors specific to the authentication process with the SOCKS5
        proxy (e.g. authentication required, invalid username or password).

        Possible sources for these exceptions include:

        Socks5AuthResult.AUTHREQ - Authentication is required - This will
        be rasied if the SOCKS5 server requires authentication and no
        username and password were supplied.

        Socks5AuthResult.EAUTHREJ - All offered authentication methods
        were rejected - This will be rasied if the proxy requires a
        authentication method which is not supported by this package.

        Socks5AuthResult.EAUTHFAIL - Unknown username or invalid
        password - Authentication failed.
    """
    def __str__(self):
        return '[%s] %s' % (self.args[0], Socks5AuthResult.MSG[self.args[0]])


class Socks4Error(ProxyError):
    """ Errors specific to the SOCKS4 proxy (e.g. request rejected).

        Possible sources for these exceptions include:

        Socks4Result.EREJECT - Request rejected or failed - Will be
        raised in the event of a failure for any reason other than the
        two following errors.

        Socks4Result.EIDCONN - Request rejected because SOCKS server
        cannot connect to identd on the client - The SOCKS4 server tried
        an ident lookup on your computer and has failed.  In this case,
        you should run an identd server and/or configure your firewall
        to allow incoming connections to local port 113 from the proxy server.

        Socks4Result.EIDDIFF - Request rejected because the client
        program and identd report different user-ids - The SOCKS4 server
        performed an ident lookup on your computer and received a different
        userid than the one you provided. Change your userid (through the
        username parameter of the setproxy method) to match and try again.
    """
    def __str__(self):
        return '[%s] %s' % (self.args[0] + Socks4Result.OFFSET,
                                            Socks4Result.MSG[self.args[0]])


class HTTPError(ProxyError):
    """ Errors specific to the HTTP CONNECT proxy (i.e. anything other
        than a 200 OK response). """
    pass


def setdefaultproxy(proxytype=None, addr=None, port=None, rdns=True,
                    username=None, password=None):
    """ Sets a default proxy which all further socksocket objects will use,
        unless explicitly changed.
    """
    global _defaultproxy
    _defaultproxy = (proxytype, addr, port, rdns, username, password)

def socks5(addr, port=1080, rdns=True, username=None, password=None):
    """ Returns a socksocket object prepared to connect through a
        SOCKS5 proxy at addr:port.  rdns, username, and password are
        the same as with socksocket.setproxy.
    """
    s5 = socksocket()
    s5.setproxy(PROXY_TYPE_SOCKS5, addr, port, rdns, username, password)
    return s5

def socks4(addr, port=1080, rdns=True, username=None):
    """ Returns a socksocket object prepared to connect through a
        SOCKS4 proxy at addr:port.  rdns and username are the same as
        with socksocket.setproxy.  password is not used with SOCKS4
        proxies.
    """
    s4 = socksocket()
    s4.setproxy(PROXY_TYPE_SOCKS4, addr, port, rdns, username)
    return s4

def httpconn(addr, port=8080, rdns=True):
    """ Returns a socksocket object prepared to connect through a
        HTTP CONNECT proxy at addr:port.  rdns is the same as with
        socksocket.setproxy.  username and password are not used with
        HTTP CONNECT proxies.
    """
    hc = socksocket()
    hc.setproxy(PROXY_TYPE_HTTP, addr, port, rdns)
    return hc


class socksocket(socket.socket):
    """ socksocket provides a SOCKS-enabled socket.
    """
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM,
                    proto=0, _sock=None):
        """ Returns a socksocket object.  The parameters are the same as
            those of the standard library's socket.socket.  However, SOCKS
            and HTTP CONNECT only work for TCP streams.  Therefore,
            family=socket.AF_INET, type=socket.SOCK_STREAM, and proto=0 are
            the defaults for socksocket.  SOCKS and HTTP CONNECT may not
            work if these defaults are changed.
        """
        _orgsocket.__init__(self, family, type, proto, _sock)
        if _defaultproxy is not None:
            self.__proxy = _defaultproxy
        else:
            self.__proxy = (None, None, None, None, None, None)
        self.__proxysockname = None
        self.__proxypeername = None

    def __recvall(self, length):
        """ Return length bytes requested from the socket.  Blocks
            until the requested number of bytes have been received.
        """
        data = bytes()
        while len(data) < length:
            d = self.recv(length - len(data))
            if not d:
                raise GeneralProxyError(GeneralResult.ENOTCONN)
            data = data + d
        return data

    def _bytes_to_ords(self, byte_seq):
        """ Return a tuple of the ordinal values of byte_seq.

            Python3 treats single cell slices of bytes as an integer
            value (e.g. b'\x01\x02'[0] == 1) while Python2 treats it
            as a str (e.g. b'\x01\x02'[0] == '\x01').  To solve this
            discrepancy, if bytes is str (i.e. Py2), get the ord() of
            each character.  If bytes is not str (e.g. Py3), the
            individual cell value is an int.  Put these int values from
            either source into a tuple so that arithmetic comparison can
            be done on the separate values.
        """
        if bytes is str:
            return tuple(x for x in map(ord, byte_seq)) # Py2
        else:
            return tuple(x for x in byte_seq) # Py3

    def __negotiatesocks5(self, destaddr, destport):
        """ Negotiate a connection through a SOCKS5 server.  destaddr
            is the IP address or domain name of the proxy server and
            destport is the port on the proxy to which a connection
            should be made.
        """
        # First we'll send the authentication packages we support.
        if (self.__proxy[4] is not None) and (self.__proxy[5]is not None):
            # The username/password details were supplied to the
            # setproxy method so we support the USERNAME/PASSWORD
            # authentication (in addition to the standard none).
            self.sendall(b'\x05\x02\x00\x02')
        else:
            # No username/password were entered, therefore we
            # only support connections with no authentication.
            self.sendall(b'\x05\x01\x00')
        # We'll receive the server's response to determine which
        # method was selected
        chosenauth = self._bytes_to_ords(self.__recvall(2))
        if chosenauth[0] != 5:   # magic byte "\x05"
            self.close()
            raise GeneralProxyError(GeneralResult.EINVALID)
        # Check the chosen authentication method
        if chosenauth[1] == 0:   # magic byte "\x00"
            # No authentication is required
            pass
        elif chosenauth[1] == 2:   # magic byte "\x02"
            # Okay, we need to perform a basic username/password
            # authentication.
            self.sendall(b'\x01' +
                            chr(len(self.__proxy[4])).encode() +
                            self.__proxy[4].encode() +
                            chr(len(self.__proxy[5])).encode() +
                            self.__proxy[5].encode()
                        )
            authstat = self._bytes_to_ords(self.__recvall(2))
            if authstat[0] != 1:   # magic byte "\x01"
                # Bad response
                self.close()
                raise GeneralProxyError(GeneralResult.EINVALID)
            if authstat[1] != 0:   # magic byte "\x00"
                # Authentication failed
                self.close()
                raise Socks5AuthError(Socks5AuthResult.EAUTHFAIL)
            # Authentication succeeded
        else:
            # Reaching here is always bad
            self.close()
            if chosenauth[1] == 255:   # magic byte "\xFF"
                raise Socks5AuthError(Socks5AuthResult.EAUTHREJ)
            else:
                raise GeneralProxyError(GeneralResult.EINVALID)
        # Now we can request the actual connection
        req = b'\x05\x01\x00'
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            ipaddr = socket.inet_aton(destaddr)
            req = req + b'\x01' + ipaddr
        except socket.error:
            # Well it's not an IP number,  so it's probably a DNS name.
            if self.__proxy[3] is True:
                # Resolve remotely
                ipaddr = None
                req = (req + b'\x03' +
                        chr(len(destaddr)).encode() + destaddr.encode())
            else:
                # Resolve locally
                ipaddr = socket.inet_aton(socket.gethostbyname(destaddr))
                req = req + b'\x01' + ipaddr
        req = req + struct.pack(">H", destport)
        self.sendall(req)
        # Get the response
        resp = self._bytes_to_ords(self.__recvall(4))
        if resp[0] != 5:   # magic byte "\x05"
            self.close()
            raise GeneralProxyError(GeneralResult.EINVALID)
        elif resp[1] != 0:   # magic byte "\x00"
            # Connection failed
            self.close()
            if resp[1] <= 8:
                raise Socks5Error(resp[1])
            else:
                raise Socks5Error(Socks5Result.UNKNOWN)
        # Get the bound address/port
        elif resp[3] == 1:   # magic byte "\x01"
            boundaddr = self.__recvall(4)
        elif resp[3] == 3:   # magic byte "\x03"
            resp = resp + self._bytes_to_ords(self.recv(1))
            boundaddr = self.__recvall(resp[4])
        else:
            self.close()
            raise GeneralProxyError(GeneralResult.EINVALID)
        boundport = struct.unpack(">H", self.__recvall(2))[0]
        self.__proxysockname = (boundaddr, boundport)
        if ipaddr is not None:
            self.__proxypeername = (socket.inet_ntoa(ipaddr), destport)
        else:
            self.__proxypeername = (destaddr, destport)

    def __negotiatesocks4(self, destaddr, destport):
        """ Negotiate a connection through a SOCKS4 server.  destaddr
            is the IP address or domain name of the proxy server and
            destport is the port on the proxy to which a connection
            should be made.
        """
        # Check if the destination address provided is an IP address
        rmtrslv = False
        try:
            ipaddr = socket.inet_aton(destaddr)
        except socket.error:
            # It's a DNS name. Check where it should be resolved.
            if self.__proxy[3] is True:
                ipaddr = b'\x00\x00\x00\x01'
                rmtrslv = True
            else:
                ipaddr = socket.inet_aton(socket.gethostbyname(destaddr))
        # Construct the request packet
        req = b'\x04\x01' + struct.pack(">H", destport) + ipaddr
        # The username parameter is considered userid for SOCKS4
        if self.__proxy[4] is not None:
            req = req + self.__proxy[4].encode()
        req = req + b'\x00'
        # DNS name if remote resolving is required
        # NOTE: This is actually an extension to the SOCKS4 protocol
        # called SOCKS4A and may not be supported in all cases.
        if rmtrslv is True:
            req = req + destaddr.encode() + b'\x00'
        self.sendall(req)
        # Get the response from the server
        resp = self.__recvall(8)
        ord_resp = self._bytes_to_ords(resp)
        if ord_resp[0] != 0:   # magic byte "\x00"
            # Bad data
            self.close()
            raise GeneralProxyError(GeneralResult.EINVALID)
        if ord_resp[1] != 90:   # magic byte "\x5A"
            # Server returned an error
            self.close()
            if (ord_resp[1] - Socks4Result.OFFSET) in (1, 2, 3):
                self.close()
                raise Socks4Error(ord_resp[1] - Socks4Result.OFFSET)
            else:
                raise Socks4Error(Socks4Result.UNKNOWN)
        # Get the bound address/port
        self.__proxysockname = (socket.inet_ntoa(resp[4:]),
                                    struct.unpack(">H", resp[2:4])[0])
        if rmtrslv is not False:
            self.__proxypeername = (socket.inet_ntoa(ipaddr), destport)
        else:
            self.__proxypeername = (destaddr, destport)

    def __negotiatehttp(self, destaddr, destport):
        """ Negotiate a connection through an HTTP proxy.  destaddr
            is the IP address or domain name of the proxy server and
            destport is the port on the proxy to which a connection
            should be made.
        """
        # If we need to resolve locally, we do this now
        if self.__proxy[3] is False:
            addr = socket.gethostbyname(destaddr)
        else:
            addr = destaddr
        self.sendall(b'CONNECT ' +
                     addr.encode() + b':' + str(destport).encode() +
                     b' HTTP/1.1\r\n' +
                     b'Host: ' + destaddr.encode() +
                     b'\r\n\r\n')
        # We read the response until we get the string "\r\n\r\n"
        resp = self.recv(1).decode()
        while resp.find("\r\n\r\n") == -1:
            resp = resp + self.recv(1).decode()
        # We just need the first line to check if the connection
        # was successful
        statusline = resp.splitlines()[0].split(" ", 2)
        if statusline[0] not in ("HTTP/1.0", "HTTP/1.1"):
            self.close()
            raise GeneralProxyError(GeneralResult.EINVALID)
        try:
            statuscode = int(statusline[1])
        except ValueError:
            self.close()
            raise GeneralProxyError(GeneralResult.EINVALID)
        if statuscode != 200:
            self.close()
            raise HTTPError(statuscode, statusline[2])
        self.__proxysockname = ("0.0.0.0", 0)
        self.__proxypeername = (addr, destport)

    def connect(self, destpair):
        """ Connect to the specified destination through a proxy.
            destpair is a tuple of the IP address or domain name and the
            port number (identical to socket.socket.connect).  Before
            using connect, select the proxy server using setproxy.
        """
        # Do a minimal input check first
        if ((not isinstance(destpair, (list, tuple))) or
                (len(destpair) < 2) or
                (not isinstance(destpair[0], str)) or
                (not isinstance(destpair[1], int))):
            raise GeneralProxyError(GeneralResult.EBADINPUT)
        if self.__proxy[0] == PROXY_TYPE_SOCKS5:
            if self.__proxy[2] is not None:
                portnum = self.__proxy[2]
            else:
                portnum = 1080
            _orgsocket.connect(self, (self.__proxy[1], portnum))
            self.__negotiatesocks5(destpair[0], destpair[1])
        elif self.__proxy[0] == PROXY_TYPE_SOCKS4:
            if self.__proxy[2] is not None:
                portnum = self.__proxy[2]
            else:
                portnum = 1080
            _orgsocket.connect(self, (self.__proxy[1], portnum))
            self.__negotiatesocks4(destpair[0], destpair[1])
        elif self.__proxy[0] == PROXY_TYPE_HTTP:
            if self.__proxy[2] is not None:
                portnum = self.__proxy[2]
            else:
                portnum = 8080
            _orgsocket.connect(self, (self.__proxy[1], portnum))
            self.__negotiatehttp(destpair[0], destpair[1])
        elif self.__proxy[0] is None:
            _orgsocket.connect(self, (destpair[0], destpair[1]))
        else:
            raise GeneralProxyError(GeneralResult.EBADPROXYTYPE)

    def getproxysockname(self):
        """ Returns the bound IP address and port number at the proxy.
        """
        return self.__proxysockname

    def getproxypeername(self):
        """ Returns the IP address and port number of the proxy.
        """
        return _orgsocket.getpeername(self)

    def getpeername(self):
        """ Returns the IP address and port number of the destination
            machine (note: getproxypeername returns the proxy).
        """
        return self.__proxypeername

    def setproxy(self, proxytype=None, addr=None, port=None, rdns=True,
                    username=None, password=None):
        """ Sets the proxy to be used.

            proxytype is one of PROXY_TYPE_SOCKS4 (including socks4a),
            PROXY_TYPE_SOCKS5, or PROXY_TYPE_HTTP.

            addr is the address (IP or domain name) of the proxy server.
            port is the port of the proxy server.  Defaults to 1080 for
            SOCKS servers and 8080 for HTTP proxy servers.

            When rdns is True (the default), DNS queries will be
            performed on the remote (server) side, rather than locally.
            Note: for DNS queries, SOCKS4 servers use an extension to the
            protocol, called SOCKS4A, which may not be supported on all
            servers.  SOCKS5 and HTTP CONNECT proxies support remote DNS.

            The username parameter is available to authenticate with
            SOCKS5 and SOCKS4 proxy servers which require authentication.
            The default is for no authentication as not all proxies
            require it.  HTTP CONNECT proxies do not support authentication.

            The password parameter only works with SOCKS5 authentication.
            And only if a username is also supplied.

            Examples:

                >>> import neehi as socks
                >>> s1 = socks.socksocket()
                # ready for connecting through a SOCKS5 proxy
                >>> s1.setproxy(socks.PROXY_TYPE_SOCKS5, "proxy.example.com")
                >>> s2 = socks.socksocket()
                # ready for connecting through an HTTP proxy on port 8000 with local DNS
                >>> s2.setproxy(socks.PROXY_TYPE_HTTP, '10.20.30.100', 8000, False)
        """
        self.__proxy = (proxytype, addr, port, rdns, username, password)

