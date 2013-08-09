#!/usr/bin/env python3
"""
PYIDSERVER.PY
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of IDServer, a command-line tool
to query an internet server and return information
about it.
"""

import sys
import os
import socket

try:
    from plib.io.classes import chat_replies
    print("Using plib.io")

except ImportError:
    
    import asyncore
    
    class chat_replies(asyncore.dispatcher):
        
        bufsize = 4096
        
        def __init__(self, addr, items,
                     connect_fn=None, close_fn=None):
            
            asyncore.dispatcher.__init__(self)
            self._addr = addr
            self._items = list(items)
            self._next_item = b""
            self._reply = b""
            self._read_complete = False
            self._connect_fn = connect_fn
            self._close_fn = close_fn
        
        def handle_connect(self):
            if self._connect_fn:
                self._connect_fn()
        
        def readable(self):
            return not (self.connected and self._next_item)
        
        def writable(self):
            return (not self.connected) or bool(self._next_item)
        
        def handle_read(self):
            data = self.recv(self.bufsize)
            self._reply += data
            # This is not a foolproof way of detecting that the read
            # is complete, but it's the best we can do
            if len(data) < self.bufsize:
                self._read_complete = True
        
        def handle_write(self):
            sent = self.send(self._next_item)
            self._next_item = self._next_item[sent:]
        
        def handle_close(self):
            # This is a wart in the asyncore API, we have to override
            # a method that already calls self.close just to eliminate
            # logging of an "unhandled close event"; also note that we
            # have to remember to call this *instead* of close() when
            # we want to close the channel, which is a weird API
            self._read_complete = True
            self.close()
        
        def __iter__(self):
            try:
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connect(self._addr)
                
                while self._items:
                    self._next_item = self._items.pop(0)
                    if self._next_item is None:
                        self._next_item = b""
                    
                    # This is another wart in the asyncore API, we have
                    # to check read_complete after *each* loop instead
                    # of just giving the loop a callback to tell it when
                    # to exit, as is done in PLIB3.IO; note also that we
                    # have to set _read_complete to True in handle_close
                    # above so closing the channel will break us out of
                    # the loop here; we can't just check for self.connected
                    # in the while condition because it will be False if
                    # a connect is still pending (i.e., the connect call
                    # above returned with the connection half-complete,
                    # and it won't be flagged complete until the first
                    # read or write event on the socket in the asyncore
                    # loop function); PLIB3.IO explicitly exposes this
                    # condition with a connect_pending flag
                    while not self._read_complete:
                        asyncore.loop(count=1)
                    
                    # Cough up whatever data we obtained
                    if self._reply:
                        yield self._reply
                    
                    # Don't continue if connection was closed
                    if not self.connected:
                        break
                    
                    self._reply = b""
                    self._read_complete = False
            
            finally:
                self.handle_close()
                if self._close_fn:
                    self._close_fn()
    
    print("Using asyncore")


def do_output(fileobj, s, linesep=True):
    fileobj.write(s)
    if linesep:
        fileobj.write(os.linesep)
    fileobj.flush()


PROTO_DEFAULT = 'http'

quitmsgs = [None, b"QUIT\r\n"]

protocols = {
    'ftp': (21, [None]),
    'http': (80, [b"HEAD / HTTP/1.0\r\n\r\n"]),
    'imap': (143, [None, b"A1 CAPABILITY\r\n", b"A2 LOGOUT\r\n"]),
    'news': (119, quitmsgs),
    'pop': (110, quitmsgs),
    'smtp': (25, quitmsgs)
}


def run_idserver(url, dns_only, protocol, portnum, fileobj):
    
    if '://' in url:
        addrtype, url = url.split('://')
        if addrtype in protocols:
            if protocol:
                do_output(fileobj,
                          "URL includes protocol {}, ignoring specified protocol {}.".format(
                          addrtype, protocol))
            protocol = addrtype
        elif addrtype:
            do_output(fileobj,
                      "URL includes incorrect protocol {}, ignoring.".format(
                      addrtype))
    if '/' in url:
        url, path = url.split('/')
        if path:
            do_output(fileobj, "URL includes path, ignoring.")
    if ':' in url:
        url, portstr = url.split(':')
        try:
            p = int(portstr)
        except ValueError:
            do_output(fileobj,
                      "URL includes invalid port {}, ignoring.".format(
                      portstr))
        else:
            if p != portnum:
                if portnum != 0:
                    do_output(fileobj,
                              "URL includes port {:d}, ignoring specified port {:d}.".format(
                              p, portnum))
                portnum = p
    
    if dns_only:
        do_output(fileobj, "Doing DNS lookup on {} ...".format(url))
    else:
        proto_msg = port_msg = ""
        if protocol == "":
            protocol = PROTO_DEFAULT
        else:
            protocol = protocol.lower()
            proto_msg = " using {}".format(protocol)
        if protocol in protocols:
            proto_port, proto_items = protocols[protocol]
            if portnum == 0:
                portnum = proto_port
            else:
                port_msg = " on port {:d}".format(portnum)
        else:
            raise ValueError("Invalid protocol: {}.".format(protocol))
    
    dns_failed = False
    try:
        ipaddr = socket.gethostbyname(url)
        if ipaddr == url:
            # URL was an IP address, reverse lookup
            try:
                hostname = socket.gethostbyaddr(ipaddr)[0]
            except socket.herror:
                hostname = "cannot be found"
            else:
                hostname = "is {}".format(hostname)
            do_output(fileobj, "Domain name for {} {}.".format(
                ipaddr, hostname))
        else:
            # URL was a domain name, normal lookup
            do_output(fileobj, "IP address for {} is {}.".format(
                url, ipaddr))
    except (socket.herror, socket.gaierror) as e:
        dns_failed = True
        do_output(fileobj, "DNS lookup failed for {}.".format(url))
        do_output(fileobj, "Error info: {}".format(str(e)))
    
    if not (dns_only or dns_failed):
        do_output(fileobj, "Contacting {}{}{} ...".format(url, proto_msg, port_msg))
        try:
            for reply in chat_replies((url, portnum), proto_items,
                                    connect_fn=lambda: do_output(
                                        fileobj,
                                        "Connected ...{}Server returned the following:{}".format(
                                        os.linesep, os.linesep)),
                                    close_fn=lambda: do_output(
                                        fileobj,
                                        "{}Connection closed.".format(os.linesep))):
                do_output(fileobj, reply.decode(), False)
        except socket.error as e:
            do_output(fileobj, "Connection failed to {}.".format(url))
            do_output(fileobj, "Error info: {}".format(str(e)))


def run_main(url, outfile=None, errfile=None,
             dns_only=False, protocol="", portnum=0):
    """Query server and write results to a file-like object.
    
    This is the intended external API for pyidserver; it wraps the
    ``run_idserver`` function, which does the work, with reasonable
    error handling and diagnostic output.
    
    The purpose of pyidserver is to query an internet server for
    basic information, and output it to the user. It does not actually
    "speak" any of the specific protocols for which it will query a
    server; it relies on the fact that most servers return some sort
    of informational "greeting" when a client connects to them, and
    the information it outputs is taken from such greetings.
    
    In the case of HTTP servers, a request must first be sent for the
    server to return any information (a HEAD request is used for this
    purpose). In the case of IMAP servers, an additional request after
    the first greeting (A1 CAPABILITY) is used to elicit additional
    information.
    
    In all cases where the session with the server is supposed to be
    explicitly terminated (all protocols supported except FTP),
    pyidserver does the termination when it is finished.
    
    Arguments:
    
    - ``url``: a URL string (either an IP address or a host name).
      May include a protocol specifier at the start (e.g., http://),
      and may include a port specifier at the end (e.g., :80). A
      trailing slash, '/', in the URL, and anything after it, are
      treated as a path specifier and ignored.
    
    - ``outfile``: the file-like object for output (actually it
      can be anything that has ``write`` and ``flush`` methods).
      Defaults to standard output.
    
    - ``errfile``: a file-like object for error output (actually it
      can be anything with a ``write`` method). Defaults to the same
      object as ``outfile``.
    
    - ``dns_only``: If true, only a DNS lookup is done; no connection
      is actually made to the server.
    
    - ``protocol: one of the strings listed as keys in the
      ``protocols`` dictionary above (the default, if nothing is
      passed, is 'http').
    
    - ``portnum``: an integer giving the port number on the server.
      (This parameter should only need to be used very rarely;
      almost always the port number is determined by the protocol
      as shown in the dictionary above.)
    """
    
    if outfile is None:
        outfile = sys.stdout
    if errfile is None:
        errfile = outfile
    try:
        run_idserver(url, dns_only, protocol, portnum, outfile)
    except:
        exc_type, exc_value, _ = sys.exc_info()
        errfile.write("{} {}{}".format(str(exc_type), str(exc_value), os.linesep))


if __name__ == '__main__':
    from plib.stdlib.options import parse_options
    
    _, __, def_dns, def_proto, def_port = run_main.__defaults__
    optlist = (
        ("-l", "--lookup", {
            'action': "store_true",
            'dest': "dns_only", 'default': def_dns,
            'help': "Only do DNS lookup, no server query"
        }),
        ("-p", "--protocol", {
            'action': "store", 'type': str,
            'dest': "protocol", 'default': def_proto,
            'help': "Use the specified protocol to contact the server"
        }),
        ("-r", "--port", {
            'action': "store", 'type': int,
            'dest': "portnum", 'default': def_port,
            'help': "Use the specified port number to contact the server"
        })
    )
    arglist = ["url"]
    
    opts, args = parse_options(optlist, arglist)
    # Spot check the parsing results
    assert opts['dns_only'] == opts.dns_only
    assert args[0] == args.url
    
    run_main(args.url, sys.stdout, sys.stderr,
             opts.dns_only, opts.protocol, opts.portnum)
