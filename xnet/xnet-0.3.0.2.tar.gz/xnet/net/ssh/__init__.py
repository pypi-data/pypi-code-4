#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

import subprocess
import sys
import re


class SSHPopenException(Exception):
    pass


class SSHPopen(subprocess.Popen):
    '''
        Add entries to ~/.ssh/environment,
        such as DISPLAY, if necessary.
    '''

    @classmethod
    def parse_ssh_nodes_file(cls, path):
        targets = []
        f = open(path)
        for line in f:
            line = line.strip()
            if line == '':
                continue
            if line.startswith('#'):
                continue
            if line.startswith('ssh://'):
                line = line[6:]
            if line.split('@', 1).__len__() != 2:
                errmsg = 'Invalid ssh address: {0}'.format(line)
                raise SSHPopenException(errmsg)
            targets.append(line)
        f.close()
        return targets

    def __init__(self, ssh_args, argv, args, user=None, host=None, env={}, **kw):
        '''
            ssh_args are additional commandline args to ssh
            argv is sys.argv
            args is non-option args of xnet tool invocation
        '''
        self._orig_argv = argv
        self._user = user
        self._host = host
        #
        if type(ssh_args) is str:
            import shlex
            ssh_args = shlex.split(ssh_args)
        if type(ssh_args) is tuple:
            ssh_args = list(ssh_args)
        assert type(ssh_args) is list
        assert not user is None
        assert not host is None
        argv = ['/usr/bin/ssh', '-t'] + ssh_args
        argv += [user + '@' + host]
        exec_argv_list = self._strip_parent_argv(self._orig_argv, args)
        exec_argv = self._list2cmdline(exec_argv_list)
        exec_argv = self._inject_env(env, exec_argv)
        argv += [exec_argv]
        super(SSHPopen, self).__init__(argv, **kw)

    def _list2cmdline(self, lst):
        exec_argv = subprocess.list2cmdline(lst)
        for ch in "()[]{}":
            exec_argv = exec_argv.replace(ch, '\\' + ch)
        return exec_argv

    def _inject_env(self, env, s):
        '''
            SECURITY PROBLEM! does not handle meta characters!
        '''
        for (key, val) in env.iteritems():
            assert not '"' in (key + val)
            assert not "'" in (key + val)
            assert not "$" in (key + val)
            assert not '\\' in (key + val)
            assert re.match('^\w+$', key)
            s = 'export {0}="{1}" && {2}'.format(key, val, s)
        return s

    def _strip_parent_argv(self, argv, args):
        '''
            On each ssh node,
            do everything in argv, except spawning new ssh nodes.

            argv is sys.argv, args is non-option args
        '''
        argv = argv[:]
        if '-z' in argv:
            i = argv.index('-z')
            del argv[i]
            del argv[i]
        if '--ssh' in argv:
            i = argv.index('--ssh')
            del argv[i]
            del argv[i]
        for (i, arg) in enumerate(argv):
            if arg.startswith('--ssh='):
                del argv[i]
                break

        #
        # Remove all non-option args from argv before remote
        # execution; these values will be trickled down and
        # distributed across nodes from the parent invocation.
        #
        for non_option_arg in args[1:]:
            while non_option_arg in argv:
                i = argv.index(non_option_arg)
                del argv[i]

        if not '-' in argv:
            argv.append('-')
        return argv


def _test():
    import doctest
    import unittest
    print(doctest.testmod())
    unittest.main()

if __name__ == "__main__":
    _test()

