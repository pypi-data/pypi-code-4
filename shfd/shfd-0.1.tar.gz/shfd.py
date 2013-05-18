# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <morgotth0@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return to Morgotth.
# ----------------------------------------------------------------------------

from __future__ import unicode_literals, print_function

"""
shfd (sh for dummies)
"""

import sys
import shlex
import subprocess
import logging

__version__ = '0.1'
__license__ = ''
__author__ = 'Morgotth'
__licence__ = 'Beerware'


IS_POSIX = sys.platform != 'win32'
IS_PY3 = sys.version_info[0] == 3

if IS_PY3:
    from io import StringIO

    unicode = str
    bytes = bytes
else:
    from StringIO import StringIO

    unicode = unicode
    bytes = str

logger = logging.getLogger('shfd')


def split_args(s, posix=IS_POSIX):
    '''parse args in string

    preserve quotes
    returns encoded args
    '''
    if IS_PY3:
        if not isinstance(s, unicode):
            # shlex only support decoded string
            s = s.decode()
    else:
        if not isinstance(s, bytes):
            # shlex only support encoded string
            s = s.encode()

    args = []
    parser = shlex.shlex(s, posix=posix)
    # split only whitespace characters
    # avoid 2>&1 => 4 tokens
    parser.whitespace_split = True
    # debug purpose
    #parser.debug = 4

    while True:
        token = parser.get_token()
        if not token:
            # None in posix mode, otherwise ''
            return args
        args.append(token)


def system_encoding():
    '''system encoding'''
    return sys.stdout.encoding


class Command(object):

    logger = logger  #.getChild('Command')

    def __init__(self, command, stdin=None, error_in_intput=False, success_required=False, shell=False):
        self.shell = shell
        self.success_required = success_required
        self.retcode = None
        self.error_in_intput = error_in_intput

        # streams
        self.stdin = stdin
        self.out = None
        self.err = None

        self.encoding = system_encoding() or 'utf8'
        self.command = unicode(command)
        self.args = split_args(command)
        self.history = []
        self.logger.debug('args: %s => %s' % (command, self.args))

    def run(self, **kwargs):
        '''

        returns (stdout, stderr,)'''
        # create process
        process = subprocess.Popen(
            self.args,
            universal_newlines=True,
            shell=self.shell,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr= (subprocess.STDOUT if self.error_in_intput else subprocess.PIPE),
            # unbuffered call: read and write are one system call
            bufsize=0,
            **kwargs
        )

        # get stdin
        if isinstance(self.stdin, Command):
            stdin = self.stdin.run().out
            if self.stdin.retcode != 0 and self.success_required:
                # error: don't execute command
                return self
            if self.stdin.success_required is True and self.stdin.retcode is None:
                # search last command without success_required
                cmd = None
                i = len(self.history) - 1
                while cmd is None and i >= 0:
                    if self.history[i].success_required is False:
                        cmd = self.history[i]
                    i -= 1
                if cmd is None or self == cmd:
                    # all commands invalid
                    raise ValueError(
                        'no command without success_required=False, invalid pattern %s'\
                            % self.history
                    )
                stdin = cmd.out
                if stdin is None:
                    raise ValueError('Invalid stdout for %s' % cmd)
                self.logger.debug('take valid command %s' % cmd)
        else:
            stdin = self.stdin

        # python 2.6 and 3.1 support
        if isinstance(stdin, unicode):
            if not IS_PY3 or sys.version_info[1] < 3:
                stdin = stdin.encode()
        # execute process
        self.logger.debug('run: %s' % (self))
        self.out, self.err = process.communicate(stdin)
        self.retcode = process.returncode

        # decode returns
        if not isinstance(self.out, unicode):
            self.out = self.out.decode(self.encoding)
        if self.err is not None and not isinstance(self.err, unicode):
            self.err = self.err.decode(self.encoding)

        return self

    def strip(self, *args, **kwargs):
        if self.retcode is not None:
            self.out = self.out.strip(*args, **kwargs)
            self.err = self.err.strip(*args, **kwargs)
        return self

    def __and__(self, other):
        if isinstance(other, Command):
            # cmd(...) & cmd(...) syntax
            other.stdin = self
            other.success_required = True
        else:
            # cmd(...) & "..." syntax
            other = Command(other, stdin=self, success_required=True)

        # complete command
        other.command = '%s & %s' % (self.command, other.command)
        # and history
        other.history = [i for i in self.history]
        other.history.append(self)

        return other

    def __or__(self, other):
        if isinstance(other, Command):
            # cmd(...) | cmd(...) syntax
            other.stdin = self
        else:
            # cmd(...) | "..." syntax
            other = Command(other, stdin=self)

        # complete command
        other.command = '%s | %s' % (self.command, other.command)
        # and history
        other.history = [i for i in self.history]
        other.history.append(self)

        return other

    def __eq__(self, other):
        if isinstance(other, Command):
            other = other.args
        else:
            other = split_args(other)
        return self.args == other

    # __str__ and __repr__

    def __unicode__(self):
        return self.command

    def __str__(self):
        return unicode(self)

    if IS_PY3:
        __str__ = __unicode__

    def __repr__(self):
        return '<Command: {cmd}>'.format(
            cmd=self.command,
        )

# Command alias
cmd = Command


def run(args):
    '''Executes a given commmand and returns streams.'''
    command = Command(args)
    return command.run()
