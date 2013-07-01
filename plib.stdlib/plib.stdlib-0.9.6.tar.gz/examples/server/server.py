#!/usr/bin/env python
"""
SERVER.PY
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A demonstration server using the self-pipe trick to trap
a shutdown signal and gracefully exit.
"""

import sys
import select
import signal
import socket
from errno import EINTR, ERESTART
from functools import partial
from SocketServer import TCPServer, BaseRequestHandler

from plib.stdlib.classes import SelfPipe, SigIntMixin

PROCESS = 1
THREAD = 2


class DemoRequestHandler(BaseRequestHandler):
    
    def handle(self):
        print "Got request", self.request, "from", self.client_address, "for", self.server
        sys.stdout.flush()
        sys.stderr.flush()


class DemoServer(SigIntMixin, TCPServer):
    
    allow_reuse_address = True
    
    wrapper_class = pipe = None
    
    def __init__(self, server_address, handler_class, use_pipe, test_race):
        self.__shutdown_flag = False
        if self.wrapper_class:
            self.wrapper_class.shutdown_with_parent = True
        self.use_pipe = use_pipe
        self.test_race = test_race
        self.setup_handlers()
        TCPServer.__init__(self, server_address, handler_class)
    
    def term_sig_handler(self, sig, frame=None):
        print "Terminate signal received by handler"
        SigIntMixin.term_sig_handler(self, sig, frame)
    
    def sig_handler(self, sig):
        if sig in self.term_sigs:
            print "Terminate signal received through pipe"
            self.terminate_process()
    
    def setup_handlers(self):
        if self.use_pipe:
            self.pipe = SelfPipe(self.sig_handler)
            self.pipe.track_signals(*self.term_sigs)
        else:
            self.setup_term_sig_handler()
    
    def setup_child(self, child):
        pass
    
    def cleanup_request(self, request, client_address):
        pass
    
    def process_request(self, request, client_address):
        if self.wrapper_class:
            child = self.wrapper_class(TCPServer.process_request,
                                       self, request, client_address)
            self.setup_child(child)
            print "Starting child", child
            child.start()
            self.cleanup_request(request, client_address)
        else:
            TCPServer.process_request(self, request, client_address)
    
    def terminate_process(self):
        self.__shutdown_flag = True
    
    def serve_forever(self):
        # We won't be using the built-in shutdown mechanism of TCPServer
        # since it gives us no way to access it using the self-pipe trick
        # (at least, not without spawning a separate thread just to call
        # shutdown, to avoid deadlock!), so we override this; note that
        # we can't use the built-in handle_request method either, since it
        # also gives no way to select on the pipe
        
        while not self.__shutdown_flag:
            if self.test_race:
                # This demonstrates a race condition between receiving a
                # signal and starting the select call below; using a
                # standard signal handler, a Ctrl-C during the sleep
                # call below will not terminate the server; it will
                # simply interrupt the sleep call and go into the select
                # call, which will block until a request is received,
                # and *then* the program will terminate *after* handling
                # the request; the self-pipe trick removes this bug, a
                # Ctrl-C during the sleep will terminate the server
                # immediately, even if there is a request pending
                from time import sleep
                self.test_race = False
                sleep(10)
            try:
                r, w, e = select.select(
                    [self.pipe, self] if self.pipe else [self],
                    [], []
                )
                if self.pipe in r:
                    self.pipe.receive_signals()
                    # go to top of loop to check shutdown flag now
                elif self in r:
                    self._handle_request_noblock()
            except (socket.error, select.error) as e:
                if e.args[0] in (EINTR, ERESTART):
                    print "System call interrupted"
                    continue
                else:
                    self.handle_error()


def server_class(opts, args):
    
    if opts.childtype == PROCESS:
        from plib.stdlib.comm._processwrapper import ProcessWrapper
        from plib.stdlib.classes import SigChldMixin
        from plib.stdlib.decotools import wraps_class
        
        @wraps_class(DemoServer)
        class _Server(SigChldMixin, DemoServer):
            
            wrapper_class = ProcessWrapper
            
            def child_sig_handler(self, sig, frame=None):
                print "Child exit signal received by handler"
                SigChldMixin.child_sig_handler(self, sig, frame)
            
            def sig_handler(self, sig):
                if sig == signal.SIGCHLD:
                    print "Child exit signal received through pipe"
                    self.reap_children()
                else:
                    DemoServer.sig_handler(self, sig)
            
            def setup_handlers(self):
                DemoServer.setup_handlers(self)
                if hasattr(signal, 'SIGCHLD'):
                    if self.use_pipe:
                        self.pipe.track_signal(signal.SIGCHLD, reset=True)
                    else:
                        self.setup_child_sig_handler()
            
            def setup_child(self, child):
                self.track_child(child)
            
            def check_child(self, child):
                return child.check()
            
            def end_child(self, child):
                child.end()
            
            def cleanup_request(self, request, client_address):
                # Only the child process needs the request open now
                self.close_request(request)
    
    elif opts.childtype == THREAD:
        from plib.stdlib.comm._threadwrapper import ThreadWrapper
        from plib.stdlib.decotools import wraps_class
        
        @wraps_class(DemoServer)
        class _Server(DemoServer):
            
            wrapper_class = ThreadWrapper
            
            def check_child(self, child):
                return child.check()
            
            def end_child(self, child):
                child.end()
    
    else:
        _Server = DemoServer
    
    return partial(_Server,
                   ("localhost", int(args.portnum)),
                   DemoRequestHandler,
                   opts.use_pipe, opts.test_race)


server_optlist = (
    ('-p', '--process', {
        'action': 'store_const', 'const': PROCESS,
        'dest': 'childtype', 'default': 0,
        'help': "fork child process for worker"
    }),
    ('-r', '--race', {
        'action': 'store_true',
        'dest': 'test_race', 'default': False,
        'help': "test for race condition between signal handler and select"
    }),
    ('-t', '--thread', {
        'action': 'store_const', 'const': THREAD,
        'dest': 'childtype', 'default': 0,
        'help': "start child thread for worker"
    }),
    ('-u', '--use-pipe', {
        'action': 'store_true',
        'dest': 'use_pipe', 'default': False,
        'help': "use the self-pipe trick"
    })
)

server_arglist = ["portnum"]


if __name__ == '__main__':
    from plib.stdlib.options import parse_options
    
    opts, args = parse_options(server_optlist, server_arglist)
    
    server_class(opts, args)().serve_forever()
