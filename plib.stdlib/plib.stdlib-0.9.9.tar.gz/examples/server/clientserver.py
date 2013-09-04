#!/usr/bin/env python
"""
CLIENTSERVER.PY
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A client program for the demonstration server that forks
the server itself.
"""

import sys
import os
import select
import signal
import socket
from errno import EINTR, ERESTART

QUIT = "Q"


def run_client(portnum, shutdown):
    while True:
        cmd = raw_input("Hit Enter to connect, or type Q to quit: ")
        if cmd.encode() == QUIT:
            break
        
        else:
            # The server will print a message and close the connection immediately
            try:
                socket.create_connection(("localhost", portnum))
            except socket.error as e:
                print str(e)
            else:
                print "Connected ok"
    
    shutdown()


def run_clientserver(server_class, use_socketpair, portnum):
    if use_socketpair:
        from plib.stdlib.comm._threadwrapper import ThreadWrapper
        from plib.stdlib.comm.socketpair import fork_socketpair
        
        def sock_listener(sock):
            while True:
                try:
                    r, w, e = select.select([sock], [], [])
                    if sock in r:
                        cmd = sock.recv(4096)
                        if cmd == QUIT:
                            break
                except select.error as e:
                    if e.args[0] in (EINTR, ERESTART):
                        continue
                    else:
                        break
            
            # This signal gets handled in the main thread, so the
            # server will catch it and break out of serve_forever
            os.kill(os.getpid(), signal.SIGINT)
        
        def run_server(sock):
            listener = ThreadWrapper(sock_listener, sock)
            listener.start()
            server_class().serve_forever()
            listener.wait()  # should shut itself down after os.kill
        
        client_sock, server = fork_socketpair(run_server)
        
        def shutdown():
            client_sock.sendall(QUIT)
            server.wait()
    
    else:
        from plib.stdlib.comm._processwrapper import ProcessWrapper
        from plib.stdlib.comm.forkserver import fork_server
        
        ProcessWrapper.term_sig = signal.SIGINT  # put this into API?
        server = fork_server(server_class)
        shutdown = server.end
    
    run_client(portnum, shutdown)


if __name__ == '__main__':
    from plib.stdlib.options import parse_options
    
    from server import server_class, server_optlist, server_arglist
    
    optlist = server_optlist + (
        ('-s', '--use-socketpair', {
            'action': 'store_true',
            'dest': 'use_socketpair', 'default': False,
            'help': "use socketpair to communicate with forked server"
        }),
    )
    
    arglist = server_arglist
    
    opts, args = parse_options(optlist, arglist)
    
    run_clientserver(server_class(opts, args), opts.use_socketpair, args.portnum)
