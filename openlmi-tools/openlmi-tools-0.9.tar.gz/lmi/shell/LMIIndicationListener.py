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

    :param callback: callback, which is called, when a indication arrives
    :param tuple args: positional arguments for callback
    :param kwargs: keyword arguments for callback
    """
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

class LMIIndicationHandler(ThreadingMixIn, BaseHTTPRequestHandler):
    """
    Class representing indication handler. The class is derived from
    :py:class:`BaseHTTPRequestHandler`, because the indications are transported by http
    protocol, and from :py:class:`ThreadingMixIn`; the indication listener is designed as
    concurrent server to properly handle each incoming indication.
    """
    def do_POST(self):
        """
        Overridden method, which is called, when a indication is received. It parses the
        indication message and searches for a matching handler for the indication name.
        Each subscribed indication should have it's Destination set something similar:

        ``<schema>://<destination>/<indication_name>``

        where the ``indication_name`` is a string, which properly defines the indication.
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
    concurrent server.
    """
    daemon_threads = True

class LMIIndicationListener(object):
    """
    Class representing indication listener, which provides a unified API for the server
    startup and shutdown and for registering an indication handler.

    :param string hostname: hostname or address of the machine, where the
        indications will be delivered
    :param int port: TCP port, where the server should listen for incoming messages
    :param string certfile: path to certificate file, if SSL used
    :param string keyfile: path to key file, if SSL used
    """
    # Minimum replacable "X" characters in handler pattern string.
    HANDLER_MINIMUM_REPL_CHARS_COUNT = 8

    def __init__(self, hostname, port, certfile=None, keyfile=None):
        self._handlers = {}
        self._hostname = hostname
        self._port = port
        self._certfile = certfile
        self._keyfile = keyfile

    def __create_handler_name(self, handler_name_pattern):
        """
        Returns unique handler name by replacing "**X**" characters for random characters
        at the end of the handler_name_pattern.

        :param string handler_name_pattern: string containing replaceable characters at the end
        :returns: unique handler name
        :rtype: string
        """
        x_cnt = 0
        pattern_len = len(handler_name_pattern)
        while True:
            while handler_name_pattern[pattern_len - 1 - x_cnt] == "X":
                x_cnt += 1
            if x_cnt < LMIIndicationListener.HANDLER_MINIMUM_REPL_CHARS_COUNT:
                raise LMIHandlerNamePatternError("Not enough replaceable characters provided")
            unique_str = handler_name_pattern[:pattern_len - x_cnt] + \
                "".join(random.choice(string.ascii_uppercase + string.digits) for x in range(x_cnt))
            if not unique_str in self._handlers:
                break
        return unique_str

    def start(self):
        """
        Starts a indication listener.

        :returns: True, if the indication listener started with no errors; False otherwise
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
        :returns: flag indicating, if the indication listener is running
        :rtype: bool
        """
        return self._server_thread.is_alive()

    @property
    def hostname(self):
        """
        :returns: hostname or address, where the indication listener is waiting for
            messages
        :rtype: string
        """
        return self._hostname

    @property
    def port(self):
        """
        :returns: port, where the indication listener is waiting for messages
        :rtype: int
        """
        return self._port

    def add_handler(self, handler_name_pattern, handler, *args, **kwargs):
        """
        Registers a handler into the indication listener. Returns a string, which is used
        for the indication recognition, when a message arrives.

        :param string handler_name_pattern: string, which may contain set of "**X**"
            characters at the end of the string. The "**X**" characters will be replaced by
            random characters and the whole string will form a unique string.
        :param handler: callable, which will be executed, when a indication is received
        :param tuple args: positional arguments for the handler
        :param dictionary kwargs: keyword arguments for the handler
        :returns: handler unique name
        :rtype: string
        """
        handler_name = self.__create_handler_name(handler_name_pattern + "X" * 16)
        self._handlers[handler_name] = LMIIndicationHandlerCallback(handler, *args, **kwargs)
        return handler_name

    def remove_handler(self, name):
        """
        Removes a specified handler from the indication listener database.

        :param string name: indication name; returned by
            :py:meth:`LMIIndicationListener.add_handler`
        """
        if not name in self._handlers:
            return
        self._handlers.pop(name)
