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

import os
import sys
import code
import readline
import __builtin__

from LMIUtil import LMIPassByRef
from LMIIndication import LMIIndication
from LMIIndicationListener import LMIIndicationListener
from LMIBaseClient import LMIBaseClient
from LMIShellClient import LMIShellClient
from LMIShellConfig import LMIShellConfig
from LMIShellOptions import LMIShellOptions
from LMISubscription import LMISubscription
from LMICompleter import LMICompleter
from LMIConnection import LMIConnection
from LMIShellConfig import LMIShellConfig
from LMIReturnValue import LMIReturnValue
from LMIObjectFactory import LMIObjectFactory

from LMIConnection import connect as connect_internal

from LMIUtil import lmi_set_use_exceptions
from LMIUtil import lmi_get_use_exceptions
from LMIUtil import lmi_isinstance

from LMIHelper import LMIHelper

class LMIConsole(code.InteractiveConsole):
    """
    Class representing an interactive console.
    """
    SHELL_PS1 = "> "
    SHELL_PS2 = "... "
    DEFAULT_LOCALS = {
        "__name__" : "__main__",
        "LMIPassByRef" : LMIPassByRef,
        "LMIIndication" : LMIIndication,
        "LMIIndicationListener" : LMIIndicationListener,
        "LMIReturnValue" : LMIReturnValue,
        "LMIBaseClient" : LMIBaseClient,
        "LMIShellClient" : LMIShellClient,
        "LMIShellConfig" : LMIShellConfig,
        "LMIShellOptions" : LMIShellOptions,
        "LMISubscription" : LMISubscription,
        "LMIConnection" : LMIConnection,
        "LMINamespace" : LMIObjectFactory().LMINamespace,
        "LMINamespaceRoot" : LMIObjectFactory().LMINamespaceRoot,
        "LMIClass" : LMIObjectFactory().LMIClass,
        "LMIInstance" : LMIObjectFactory().LMIInstance,
        "LMIInstanceName" : LMIObjectFactory().LMIInstanceName,
        "LMIMethod" : LMIObjectFactory().LMIMethod,
        "use_exceptions" : lmi_set_use_exceptions,
        "lmi_isinstance" : lmi_isinstance,
        "help" : LMIHelper()
    }

    def __init__(self):
        """
        Constructs a LMIConsole object.
        """
        # Setup default LMIConsole locals, that are needed
        # for proper object construction
        locals = dict(LMIConsole.DEFAULT_LOCALS.items())
        code.InteractiveConsole.__init__(self, locals)

        # Store configuration
        config = LMIShellConfig()
        self._history_file = config.history_file
        self._history_length = config.history_length
        self._use_cache = config.use_cache
        self._use_exceptions = config.use_exceptions
        self._verify_server_cert = True

        # Setup LMIShell-wide option, which defines, whether the LMIShell
        # should propagate caught exceptions, or dump them
        lmi_set_use_exceptions(self._use_exceptions)

    def setup_completer(self):
        """
        Initializes tab-completer.
        """
        self._completer = LMICompleter(self.locals)
        readline.set_completer(self._completer.complete)
        readline.parse_and_bind("tab: complete")

    def interact(self, locals=None):
        """
        Starts the interactive mode.

        Arguments:
            locals -- dictionary with locals
        """
        def connect(hostname, username="", password="", **kwargs):
            """
            Returns LMIConnection object with provided hostname and credentials.

            Arguments:
                hostname -- uri of the CIMOM
                username -- account, under which, the CIM calls will be performed
                password -- user's password

            Keyword Arguments:
                key_file -- string containing path to x509 key file; default value is None
                cert_file -- string containing path to x509 cert file; default value is None
                verify_server_cert -- bool flag, whether a server side certificate needs
                    to be verified, if ssl used; default value is True
            """
            key_file = kwargs.pop("key_file", None)
            cert_file = kwargs.pop("cert_file", None)
            verify_server_cert = kwargs.pop("verify_server_cert", self._verify_server_cert)
            if kwargs:
                raise TypeError("connect() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

            return connect_internal(hostname, username, password, interactive=True,
                use_cache=self._use_cache, key_file=key_file, cert_file=cert_file,
                verify_server_cert=verify_server_cert)

        # Initialize the interpreter
        if locals is None:
            locals = {}
        else:
            for (k, v) in locals.iteritems():
                if isinstance(v, LMIConnection):
                    locals[k]._client.interactive = True
        locals["clear_history"] = self.clear_history
        locals["connect"] = connect
        self.locals = dict(self.locals.items() + locals.items())
        self.setup_completer()
        self.load_history()
        old_sys_ps1 = ""
        try:
            old_sys_ps1 = sys.ps1
        except AttributeError, e:
            old_sys_ps1 = ""
        try:
            old_sys_ps2 = sys.ps2
        except AttributeError, e:
            old_sys_ps2 = ""
        sys.ps1 = LMIConsole.SHELL_PS1
        sys.ps2 = LMIConsole.SHELL_PS2

        # Interact
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, "encoding", None)
                    if encoding and not isinstance(line, unicode):
                        line = line.decode(encoding)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    more = self.push(line)
            except KeyboardInterrupt:
                self.write("\n")
                self.resetbuffer()
                more = 0

        # Cleanup after the interpreter
        if old_sys_ps1:
            sys.ps1 = old_sys_ps1
        if old_sys_ps2:
            sys.ps2 = old_sys_ps2
        self.save_history()

    def interpret(self, script_name, script_argv, locals=None):
        """
        Interprets a specified script within additional provided locals.
        There are LMIConsole.DEFAULT_LOCALS present.

        Arguments:
            script_name -- string containing a script name
            script_argv -- script CLI arguments
            locals -- dictionary with locals
        """
        # Helper function for non-interactive connect
        def connect(hostname, username="", password="", **kwargs):
            """
            Returns LMIConnection object with provided hostname and credentials.

            Arguments:
                hostname -- uri of the CIMOM
                username -- account, under which, the CIM calls will be performed
                password -- user's password

            Keyword Arguments:
                key_file -- string containing path to x509 key file; default value is None
                cert_file -- string containing path to x509 cert file; default value is None
                verify_server_cert -- bool flag, whether a server side certificate needs
                    to be verified, if ssl used; default value is True
            """
            # Set remaining arguments
            key_file = kwargs.pop("key_file", None)
            cert_file = kwargs.pop("cert_file", None)
            verify_server_cert = kwargs.pop("verify_server_cert", self._verify_server_cert)
            if kwargs:
                raise TypeError("connect() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

            return connect_internal(hostname, username, password, interactive=False,
                use_cache=self._use_cache, key_file=key_file, cert_file=cert_file,
                verify_server_cert=verify_server_cert)
        # Initialize locals
        if locals is None:
            locals = {}
        else:
            for (k, v) in locals.iteritems():
                if isinstance(v, LMIConnection):
                    locals[k]._client.interactive = False
        locals["connect"] = connect
        self.locals = dict(self.locals.items() + locals.items())

        # Execute the script
        sys.argv = script_argv
        exit_code = 0
        try:
            execfile(script_name, self.locals)
        except SystemExit, e:
            exit_code = e.code

        # Return with exit_code
        return exit_code

    def load_history(self):
        """
        Loads the shell's history from the history file.
        """
        if self._history_length == 0 or not os.path.exists(self._history_file):
            return
        readline.read_history_file(self._history_file)
        if self._history_length > 0 and readline.get_current_history_length() > self._history_length:
            readline.set_history_length(self._history_length)
            readline.write_history_file(self._history_file)
            readline.read_history_file(self._history_file)

    def save_history(self):
        """
        Saves current history of commands into the history file. If the length of history
        exceeds a maximum history file length, the history will be truncated.
        """
        if self._history_length == 0:
            return
        elif self._history_length > 0:
            readline.set_history_length(self._history_length)
        try:
            readline.write_history_file(self._history_file)
        except IOError, e:
            pass

    def clear_history(self):
        """
        Clears the current history.
        """
        readline.clear_history()

    def set_verify_server_certificate(self, verify_server_cert=True):
        """
        Turns on or off server side certificate verification, if SSL used.

        Arguments:
            verify_server_cert -- flag indicating, whether a server side certificate
                needs to be verified, if SSL used
        """
        self._verify_server_cert = verify_server_cert
