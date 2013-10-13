# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function

import sys
import inspect

import argparse

from .commands import Group, Option, InvalidCommand, Command, Shell
from .cli import prompt, prompt_pass, prompt_bool, prompt_choices

__version__ = "0.1.0"

__all__ = ["Command", "Shell", "Manager", "Group", "Option",
           "prompt", "prompt_pass", "prompt_bool", "prompt_choices"]


class Manager(object):
    """
    Controller class for handling a set of commands.

    Typical usage::

        class Print(Command):

            def run(self):
                print "hello"

        manager = Manager()
        manager.add_command("print", Print())

        if __name__ == "__main__":
            manager.run()

    On command line::

        python manage.py print
        > hello

    :param app: A variable containing context for the commands,
                or a callable that returns such a variable.
    """

    @property
    def description(self):
        description = self._description or self.__doc__
        return description.strip()

    def __init__(self, context=None, usage=None, description="", prog=None, exit_on_error=True, handle_exceptions=True):

        self._commands = dict()
        self._options = list()
        self._context = context
        self._prog = prog
        self._exit_on_error = exit_on_error
        self._handle_exceptions = handle_exceptions

        self._usage = usage
        self._description = description

        self.parent = None

    def add_option(self, *args, **kwargs):
        """
        Adds an application-wide option. This is useful if you want to set
        variables applying to the application setup, rather than individual
        commands.

        For this to work, the manager must be initialized with a factory
        function rather than an instance. Otherwise any options you set will
        be ignored.

        The arguments are then passed to your function, e.g.::

            def create_context(config=None):
                app_context = {}
                if config:
                    import simplejson
                    app_context = simplejson.load(open(config))

                return app_context

            manager = Manager(create_ctx)
            manager.add_option("-c", "--config", dest="config", required=False)

        and are evoked like this::

            > python manage.py -c dev.cfg mycommand

        Any manager options passed in the command line will not be passed to
        the command.

        Arguments for this function are the same as for the Option class.

        The return value of the function is stored in the Manager and can
        be retrieved by calling manager.context().
        """

        self._options.append(Option(*args, **kwargs))

    def create_context(self, **kwargs):
        if self.parent:
            # Sub-manager, defer to parent Manager
            return self.parent.create_context(**kwargs)

        if hasattr(self._context, '__call__'):
            return self._context(**kwargs)

        return self._context

    def context(self):
        return self._context

    def create_parser(self, prog=None, usage=None):
        """
        Creates an ArgumentParser instance from options returned
        by get_options(), and a subparser for the given command.
        """

        prog = prog or self._prog or sys.argv[0]

        parser = argparse.ArgumentParser(prog=prog, usage=usage, add_help=False)
        parser.add_argument('-h', '--help', action='store_true', default=False, help='show this help message and exit')
        for option in self.get_options():
            parser.add_argument(*option.args, **option.kwargs)

        parser.add_argument("__command", nargs=argparse.OPTIONAL, default=None, help=argparse.SUPPRESS)
        parser.add_argument("__args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

        return parser

    def get_options(self):
        if self.parent:
            return self.parent._options

        return self._options

    def add_command(self, name, command):
        """
        Adds command to registry.

        :param command: Command instance
        """

        if isinstance(command, Manager):
            command.parent = self

        self._commands[name] = command

    def command(self, func):
        """
        Decorator to add a command function to the registry.

        :param func: command function. Arguments depend on the
                     options.
        """

        args, varargs, keywords, defaults = inspect.getargspec(func)

        options = []

        # first arg is always "app" : ignore

        defaults = defaults or []
        kwargs = dict(zip(*[reversed(l) for l in (args, defaults)]))

        if sys.version_info[0] > 2:
            unicode_type = str
        else:
            unicode_type = unicode

        for arg in args:
            if arg in kwargs:

                default = kwargs[arg]

                if isinstance(default, bool):
                    options.append(Option('-%s' % arg[0],
                                          '--%s' % arg,
                                          action="store_true",
                                          dest=arg,
                                          required=False,
                                          default=default))
                else:
                    options.append(Option('-%s' % arg[0],
                                          '--%s' % arg,
                                          dest=arg,
                                          type=unicode_type,
                                          required=False,
                                          default=default))

            else:
                options.append(Option(arg, type=unicode_type))

        command = Command()
        command.run = func
        command.__doc__ = func.__doc__
        command.option_list = options

        self.add_command(func.__name__, command)

        return func

    def option(self, *args, **kwargs):
        """
        Decorator to add an option to a function. Automatically registers the
        function - do not use together with ``@command``. You can add as many
        ``@option`` calls as you like, for example::

            @option('-n', '--name', dest='name')
            @option('-u', '--url', dest='url')
            def hello(name, url):
                print "hello", name, url

        Takes the same arguments as the ``Option`` constructor.
        """

        option = Option(*args, **kwargs)

        def decorate(func):
            name = func.__name__

            if name not in self._commands:

                command = Command()
                command.run = func
                command.__doc__ = func.__doc__
                command.option_list = []

                self.add_command(name, command)

            self._commands[name].option_list.append(option)
            return func
        return decorate

    def shell(self, func):
        """
        Decorator that wraps function in shell command. This is equivalent to::

            def _make_context(app):
                return dict(app=app)

            manager.add_command("shell", Shell(make_context=_make_context))

        The decorated function should take a single "app" argument, and return
        a dict.

        For more sophisticated usage use the Shell class.
        """

        self.add_command('shell', Shell(make_context=func))

        return func

    def format_commands(self):
        """
        Returns string consisting of all commands and their descriptions.
        """

        rv = []
        
        if len(self._commands) > 0:
            pad = max(map(len, self._commands.keys())) + 2
            format = '  %%- %ds%%s' % pad

            rv.append("Available commands:")
            for name, command in sorted(self._commands.items()):
                usage = name
                description = command.description or ''
                usage = format % (name, description)
                rv.append(usage)

        return "\n".join(rv)

    def print_help(self, prog=None):
        """
        Prints help
        """

        parser = self.create_parser(prog=prog, usage=self._usage)
        print(parser.format_help())
        print(self.format_commands())

    def _get_command(self, name):
        try:
            return self._commands[name]
        except KeyError:
            raise InvalidCommand("Command %s not found" % name)

    def handle(self, name, args=None, prog=None):

        args = list(args or [])

        command = self._get_command(name)

        if isinstance(command, Manager):
            # run sub-manager
            #print "Running submanager", name
            return command.run(prog=prog + " " + name, args=args)
        else:
            command_parser = command.create_parser(prog + " " + name)
            if getattr(command, 'capture_all_args', False):
                command_namespace, unparsed_args = \
                    command_parser.parse_known_args(args)
                positional_args = [unparsed_args]
            else:
                command_namespace = command_parser.parse_args(args)
                positional_args = []

        return command.run(*positional_args, **command_namespace.__dict__)

    def run(self, commands=None, default_command=None, prog=None, args=None):
        """
        Prepares manager to receive command line input. Usually run
        inside "if __name__ == "__main__"" block in a Python script.

        :param commands: optional dict of commands. Appended to any commands
                         added using add_command().

        :param default_command: name of default command to run if no
                                arguments passed.

        :param args: list of arguments to parse (default: sys.argv[1:])
        """

        if commands:
            self._commands.update(commands)

        #print "run:", prog, "args:", args
        prog = prog or self._prog or sys.argv[0]
        if args is None:
            args = sys.argv[1:]

        self._parser = self.create_parser(prog=prog, usage=self._usage)
        manager_namespace, remaining_args = self._parser.parse_known_args(args)

        manager_args = manager_namespace.__dict__.copy()
        del(manager_args["__command"])
        del(manager_args["__args"])
        del(manager_args["help"])
        self._context = self.create_context(**manager_args)

        command = manager_namespace.__dict__["__command"]

        # handle help
        if manager_namespace.help or command == "help":
            if command is not None and command != "help":
                cmd = self._get_command(command)
                parser = cmd.create_parser(prog + " " + command)
                parser.print_help()

            else:
                self.print_help(prog=prog)

            sys.exit(0)

        else:
            command = command or default_command
            try:
                if command is None:
                    raise InvalidCommand("Missing command")

                command_args = manager_namespace.__dict__["__args"] + remaining_args
                result = self.handle(command, args=command_args, prog=prog)
                return result

            except InvalidCommand as e:
                if self._handle_exceptions:
                    print(e)
                    print()
                    self.print_help(prog=prog)
                else:
                    raise

        if self._exit_on_error:
            sys.exit(1)

