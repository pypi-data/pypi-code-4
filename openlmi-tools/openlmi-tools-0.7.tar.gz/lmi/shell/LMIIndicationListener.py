# Copyright (C) 2012-2013 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import sys
import ssl
import time
import pywbem
import random
import socket
import string
import threading

from SocketServer import BaseRequestHandler
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler

from LMIIndication import LMIIndication

from LMIExceptions import LMIHandlerNamePatternError

class LMIIndicationHandlerCallback(object):
    """
    Helper class, which stores indication handler callback with its arguments and keyword
    arguments.
    """
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

class LMIIndicationHandler(ThreadingMixIn, BaseHTTPRequestHandler):
    """
    Class representing indicatoin handler. The class is derived from
    BaseHTTPRequestHandler, because the indications are transported by http protocol,
    and from ThreadingMixIn; the indication listener is designed as concurent server to
    properly handle each incoming indication.
    """
    def do_POST(self):
        """
        Overriden method, which is called, when a indication is received. It parses the
        indication message and searches for a matching handler for the indication name.
        Each subscribed indication should have it's Destination set something similar:

        <schema>://<destination>/<indication_name>

        where the indication_name is a string, which properly defines the indication.
        """
        msg = self.rfile.read()
        tt = pywbem.parse_cim(pywbem.xml_to_tupletree(msg))
        message = tt[2]
        export_methods = {}
        if message[0].upper() != "MESSAGE":
            return
        message_params = message[2]
        if not message_params:
            return
        for param in message_params:
            if param[0].upper() != "SIMPLEEXPREQ":
                continue
            export_method_call = param[2]
            export_method_name = export_method_call[1]["NAME"]
            exp_params = export_method_call[2]
            export_method_params = {}
            for method_param in exp_params:
                export_method_params[method_param[0]] = method_param[1]
            export_methods[export_method_name] = export_method_params
        ind = LMIIndication(export_methods)
        path = self.path[1:]
        if path in self.server._handlers:
            cb = self.server._handlers[path]
            cb.callback(ind, *cb.args, **cb.kwargs)

class LMIIndicationServer(ThreadingMixIn, HTTPServer):
    """
    Class representing indication server, derived from HTTPServer and designed as
    concurent server.
    """
    daemon_threads = True

class LMIIndicationListener(object):
    """
    Class representing indication listener, which provides a unified api for the server
    startup and shutdown and for registering an indication handler.
    """
    # Minimum replacable "X" characters in handler pattern string.
    HANDLER_MINIMUM_REPL_CHARS_COUNT = 8

    def __init__(self, hostname, port, certfile=None, keyfile=None):
        """
        Constructs a LMIIndicationListener object.

        Arguments:
            hostname -- string containing a hostname or address of the machine, where the
                indications will be delivered
            port -- tcp port, where the server should listen for incoming messages
            certfile -- string containing a path to certificate file, if ssl used
            keyfile -- string containing a path to key file, if ssl used
        """
        self._handlers = {}
        self._hostname = hostname
        self._port = port
        self._certfile = certfile
        self._keyfile = keyfile

    def __create_handler_name(self, handler_name_pattern):
        """
        Returns unique handler name by replacing "X" characters for random characters
        at the end of the handler_name_pattern.

        Arguments:
            handler_name_pattern -- string containing replacable characters at the end
        """
        x_cnt = 0
        pattern_len = len(handler_name_pattern)
        while True:
            while handler_name_pattern[pattern_len - 1 - x_cnt] == "X":
                x_cnt += 1
            if x_cnt < LMIIndicationListener.HANDLER_MINIMUM_REPL_CHARS_COUNT:
                raise LMIHandlerNamePatternError("Not enough replacable characters provided")
            unique_str = handler_name_pattern[:pattern_len - x_cnt] + \
                "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(x_cnt))
            if not unique_str in self._handlers:
                break
        return unique_str

    def start(self):
        """
        Returns True, if the indication listener started with no errors; otherwise False.
        """
        try:
            self._server = LMIIndicationServer((self._hostname, self._port), LMIIndicationHandler)
        except socket.error, e:
            return False
        self._server._handlers = self._handlers
        self._server_thread = threading.Thread(target=self._server.serve_forever)
        self._server_thread.daemon = True
        if self._certfile:
            self._server.socket = ssl.wrap_socket(
                self._server.socket,
                certfile=self._certfile,
                keyfile=self._keyfile,
                server_side=True)
        self._server_thread.start()
        return True

    def stop(self):
        """
        Stops the indication listener.
        """
        self._server.shutdown()
        self._server_thread.join()

    @property
    def is_alive(self):
        """
        Property returning a bool flag indicating, if the indication listener is running.
        """
        return self._server_thread.is_alive()

    @property
    def hostname(self):
        """
        Returns a string of local hostname of address, where the indication listener is
        waiting for messages.
        """
        return self._hostname

    @property
    def port(self):
        """
        Property returning a numeric value of local port, where the indication listener is
        waiting for messages.
        """
        return self._port

    def add_handler(self, handler_name_pattern, handler, *args, **kwargs):
        """
        Registers a handler into the indication listener. Returns a string, which is used
        for the indication recognition, when a message arrives.

        Arguments:
            handler_name_pattern -- string, which may contain set of "X" characters at the
                end of the string. The "X" characters will be replaced by random
                characters and the whole string will form a unique string.
            handler -- callable, which will be called, when a indication is received
            args -- positional arguments for the handler
            kwargs -- keyword arguments for the handler
        """
        handler_name = self.__create_handler_name(handler_name_pattern + "X" * 16)
        self._handlers[handler_name] = LMIIndicationHandlerCallback(handler, *args, **kwargs)
        return handler_name

    def remove_handler(self, name):
        """
        Removes a specified handler from the indication listener database.

        Arguments:
            name -- string containing the indication name; returned by
                LMIIndicationListener.add_handler() call
        """
        if not name in self._handlers:
            return
        self._handlers.pop(name)
