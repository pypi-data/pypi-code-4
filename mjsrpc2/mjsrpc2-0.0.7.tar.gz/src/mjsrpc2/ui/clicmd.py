'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import cmd
import logging
import sys
import functools
import shlex
import argparse
import mjsrpc2

class BaseCmd(cmd.Cmd):
    def __init__(self, completekey = "tab", stdin = None, stdout = None, config = None, parent = None):
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self._config = config
        self._interactive = False
        name = getattr(self, "name", "unknown")
        self._update_context(parent, name)
        self._cmd_count = 0

    def __call__(self, cmd_text):
        if self._interactive:
            self.cmdloop()
        else:
            self.onecmd(cmd_text)

    def precmd(self, line):
        if line.strip().startswith("#"):
            line = ""
        self._cmd_count += 1
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        if line == 'EOF':
            return True
        return stop


    def add_command(self, name, handler):
        hname = str("do_%s" % name)
        handler._update_context(self, name)

        def __wrapper(command):
            hndl = handler
            if isinstance(hndl, BaseCmd):
                hndl._interactive = self._interactive
            self.log.debug("Executing: %s via %s", command, hndl)
            try:
                hndl(command)
            except mjsrpc2.RPCException, e:
                self.log.error(e)
        self.__dict__[hname] = __wrapper


    def get_names(self):
        names = dir(self)
        if 'do_EOF' in names:
            names.remove('do_EOF')
        return names

    def cmdloop(self, intro = None):
        self._interactive = True
        try:

            ret = cmd.Cmd.cmdloop(self, intro)
        except KeyboardInterrupt:
            print
            self.log.error("Keyboard interupt!")
            self.do_quit("")

        return ret

    def preloop(self):
        self._cmd_count = 0


    def _update_context(self, parent, name):
        self.name = name
        self.parent = parent
        if parent is None:
            context = name
        else:
            context = parent.name + "." + name # Show last two levels
        self.prompt = context + "> "
        self.log = logging.getLogger(context)


    def do_quit(self, cmd):
        if self.parent is None:
            self.log.info("Bye!")
            sys.exit()
        else:
            self.log.debug("quit")
            self.parent.onecmd("quit %s" % cmd)

    def do_exit(self, cmd):
        return True

    def do_EOF(self, cmd):
        print
        return self.do_exit(cmd)


    def emptyline(self):
        return ""

    def default(self, cmd_text):
        log = self.log
        log.error("Unknown command: %s", cmd_text)


class ParserError(Exception):
    def __init__(self, message = "", status = 0):
        self.message = message
        self.status = status


class FriendlyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage()
        self.exit(status = 1, message = message)

    def exit(self, status = 0, message = ""):
        raise ParserError(message, status)

def opts(func):
    log = logging.getLogger("opts")
    func._arg_parser = FriendlyArgumentParser()
    if func.__name__.startswith("do_"):
        name = func.__name__[3:]
    else:
        name = func.__name__
    func._arg_parser.prog = name
    @functools.wraps(func)
    def __wrapper(inst, command):
        parser = getattr(func, "_arg_parser", None)
        if parser is None:
            raise Exception("Internal error")
        input_cmd = shlex.split(command)
        try:
            args = parser.parse_args(input_cmd)
        except ParserError, e:
            if e.status != 0:
                log.critical("Error parsing command: %s", e.message)
            else:
                if e.message: log.info(e.message)
        else:
            return func(inst, args)

    return __wrapper

def option(*args, **kwds):
    def __handle_args(f):
        parser = getattr(f, "_arg_parser", None)
        if parser is None:
            raise Exception("Invalid usage of decorator. Use first @opts decorator")
        parser.add_argument(*args, **kwds)
        @functools.wraps(f)
        def __wrapper(*fargs, **fkwds):
            return f(*fargs, **fkwds)
        return __wrapper
    return __handle_args
