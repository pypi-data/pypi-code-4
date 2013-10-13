# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function

import os
import code

import argparse

from .cli import prompt, prompt_pass, prompt_bool, prompt_choices


class InvalidCommand(Exception):
    pass


class Group(object):
    """
    Stores argument groups and mutually exclusive groups for
    `ArgumentParser.add_argument_group <http://argparse.googlecode.com/svn/trunk/doc/other-methods.html#argument-groups>`
    or `ArgumentParser.add_mutually_exclusive_group <http://argparse.googlecode.com/svn/trunk/doc/other-methods.html#add_mutually_exclusive_group>`.

    Note: The title and description params cannot be used with the exclusive
    or required params.

    :param options: A list of Option classes to add to this group
    :param title: A string to use as the title of the argument group
    :param description: A string to use as the description of the argument
                        group
    :param exclusive: A boolean indicating if this is an argument group or a
                      mutually exclusive group
    :param required: A boolean indicating if this mutually exclusive group
                     must have an option selected
    """

    def __init__(self, *options, **kwargs):
        self.option_list = options

        self.title = kwargs.pop("title", None)
        self.description = kwargs.pop("description", None)
        self.exclusive = kwargs.pop("exclusive", None)
        self.required = kwargs.pop("required", None)

        if ((self.title or self.description) and
                (self.required or self.exclusive)):
            raise TypeError("title and/or description cannot be used with "
                                "required and/or exclusive.")

        super(Group, self).__init__(**kwargs)

    def get_options(self):
        """
        By default, returns self.option_list. Override if you
        need to do instance-specific configuration.
        """
        return self.option_list


class Option(object):
    """
    Stores positional and optional arguments for `ArgumentParser.add_argument
    <http://argparse.googlecode.com/svn/trunk/doc/add_argument.html>`_.

    :param name_or_flags: Either a name or a list of option strings,
                          e.g. foo or -f, --foo
    :param action: The basic type of action to be taken when this argument
                   is encountered at the command-line.
    :param nargs: The number of command-line arguments that should be consumed.
    :param const: A constant value required by some action and nargs selections.
    :param default: The value produced if the argument is absent from
                    the command-line.
    :param type: The type to which the command-line arg should be converted.
    :param choices: A container of the allowable values for the argument.
    :param required: Whether or not the command-line option may be omitted
                     (optionals only).
    :param help: A brief description of what the argument does.
    :param metavar: A name for the argument in usage messages.
    :param dest: The name of the attribute to be added to the object
                 returned by parse_args().
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Command(object):
    """
    Base class for creating commands.
    """

    option_list = []

    @property
    def description(self):
        description = self.__doc__ or ''
        return description.strip()

    def add_option(self, option):
        """
        Adds Option to option list.
        """
        self.option_list.append(option)

    def get_options(self):
        """
        By default, returns self.option_list. Override if you
        need to do instance-specific configuration.
        """
        return self.option_list

    def create_parser(self, prog):
        parser = argparse.ArgumentParser(prog=prog,
                                         description=self.description)

        for option in self.get_options():
            if isinstance(option, Group):
                if option.exclusive:
                    group = parser.add_mutually_exclusive_group(
                                required=option.required,
                            )
                else:
                    group = parser.add_argument_group(
                                title=option.title,
                                description=option.description,
                            )
                for opt in option.get_options():
                    group.add_argument(*opt.args, **opt.kwargs)
            else:
                parser.add_argument(*option.args, **option.kwargs)

        return parser

    def run(self):
        """
        Runs a command. This must be implemented by the subclass. Should take
        arguments as configured by the Command options.
        """
        raise NotImplementedError


class Shell(Command):
    """
    Runs a Python shell.

    :param banner: banner appearing at top of shell when started
    :param make_context: a callable returning a dict of variables
                         used in the shell namespace.
    :param use_bpython: use BPython shell if available, ignore if not.
                        The BPython shell can be turned off in command
                        line by passing the **--no-bpython** flag.
    :param use_ipython: use IPython shell if available, ignore if not.
                        The IPython shell can be turned off in command
                        line by passing the **--no-ipython** flag.
    """

    banner = ''

    description = 'Runs a Python shell.'

    def __init__(self, banner=None, make_context=None, use_ipython=True,
                use_bpython=True):

        self.banner = banner or self.banner
        self.use_ipython = use_ipython
        self.use_bpython = use_bpython

        self.make_context = make_context

    def get_options(self):
        return (
            Option('--no-ipython',
                action="store_true",
                dest='no_ipython',
                default=not(self.use_ipython)),
            Option('--no-bpython',
                action="store_true",
                dest='no_bpython',
                default=not(self.use_bpython))
        )

    def get_context(self):
        """
        Returns a dict of context variables added to the shell namespace.
        """
        return self.make_context()

    def run(self, no_ipython, no_bpython):
        """
        Runs the shell.  If no_bpython is False or use_bpython is True, then
        a BPython shell is run (if installed).  Else, if no_ipython is False or
        use_python is True then a IPython shell is run (if installed).
        """

        context = self.get_context()
        if not no_bpython:
            # Try BPython
            try:
                from bpython import embed
                embed(banner=self.banner, locals_=self.get_context())
                return
            except ImportError:
                # Try IPython
                if not no_ipython:
                    try:
                        import IPython
                        try:
                            sh = IPython.Shell.IPShellEmbed(banner=self.banner)
                        except AttributeError:
                            sh = IPython.frontend.terminal.embed.InteractiveShellEmbed(banner1=self.banner)
                        sh(global_ns=dict(), local_ns=context)
                        return
                    except ImportError:
                        pass

        # Use basic python shell
        code.interact(self.banner, local=context)


class Clean(Command):
    "Remove *.pyc and *.pyo files recursively starting at current directory"
    def run(self):
        for dirpath, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                if '.pyc' or '.pyo' in filename:
                    full_pathname = os.path.join(dirpath, filename)
                    print('Removing %s' % full_pathname)
                    os.remove(full_pathname)


