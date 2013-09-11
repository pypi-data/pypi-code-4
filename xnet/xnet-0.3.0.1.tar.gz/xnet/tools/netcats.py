#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#

__all__ = ['NetcatsTool']

import unittest
import doctest
import sys
import os
import socket
import fcntl
import gevent
from gevent import select
#from gevent.socket import wait_read

from xnet.tools import Tool
from xnet.tools import VerbosityPrinter
from xnet.net.ipv4 import IPRangeIterator


def _get_output_filepath(item, base):
    #
    # item is the result of some specific processing
    # and may contain arbitrary meta characters
    # which should not affect the file system path
    # where the output file is created.
    #
    item = item.replace('/', '__')
    item = item.replace('\\', '--')
    path = base + item
    return path


class NetcatsException(Exception):
    pass


class NetcatsTool(Tool):
    '''
        NetcatsTool
            Default format is:
                {addr} {port} [data received from remote host...]

            Input from stdin is sent to all hosts. Each line of
            output from remote host is prefixed by what __format__()
            returns.
    '''

    __toolname__ = 'netcat'
    __itemname__ = 'host'
    __description__ = 'multi-peer netcat-like tool'

    cmdline_options = [
        ('-p', '--port', 'TCP port to connect to',
            dict(dest='port')),
        ('', '--tag-lines', 'tag output lines with target address',
            dict(dest='tag_lines', action='store_true')),
        #('-O', '--open', 'print only results for open ports',
        #    dict(dest='open')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __init__(self, options, outfile=sys.stdout, *args, **kw):
        super(NetcatsTool, self).__init__(options, *args, **kw)
        self._outfile = outfile
        self._stdin_pipe = self._nonblocking_pipe()
        self._addr = None
        self._port = 80
        if not self.options.port is None:
            self._port = int(self.options.port)
        self._recv_buffer = ''

    def __del__(self):
        os.close(self._stdin_pipe[0])
        os.close(self._stdin_pipe[1])
        #if not self._outfile in (sys.stdout, sys.stderr):
        #    self._outfile.close()

    def _nonblocking_pipe(self):
        pipe = os.pipe()
        fcntl.fcntl(pipe[0], fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(pipe[1], fcntl.F_SETFL, os.O_NONBLOCK)
        return pipe

    @classmethod
    def __massage__(self, iterator, options):
        for item in iterator:
            item = item.strip()
            try:
                iprangeiter = IPRangeIterator(item)
            except ValueError:
                yield item
            else:
                for ip in iprangeiter:
                    yield str(ip)

    def __parse__(self, item, iterator):
        host = self._host = item.strip()
        addr = (host, self._port)
        self._addr = addr  # for __timeout__()
        result = {'addr': addr}
        return result

    def __action__(self, parse_result):
        addr = parse_result['addr']
        sock = None
        socket_error = None
        result = {}
        #
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(addr)
        except socket.error, e:
            errmsg = e.strerror.lower()
            self.set_error(errmsg)
            return
        self.vprint_stderr(1, '[connected to {0}:{1}]'.format(*addr))

        outfile = sys.stdout
        if self.options.split_output:
            path = _get_output_filepath(self._host, self.options.split_output)
            outfile = open(path, 'wb')
            fcntl.fcntl(outfile.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        self._outfile = outfile

        done = False
        stdin = self._stdin_pipe[0]
        while not done and not sock is None:
            try:
                rfds = [stdin, sock]
                rlist, _, _ = select.select(rfds, [], [])
                if stdin in rlist:
                    data = os.read(stdin, 4096)
                    if len(data) > 0:
                        sock.send(data)
                    else:
                        done = True
                if sock in rlist:
                    data = sock.recv(4096)
                    if len(data) > 0:
                        if self.options.tag_lines:
                            tag = '\n' + self._host + ':'
                            data = tag + tag.join(data.split('\n'))
                        #
                        # Handle random exceptions on file-io
                        # in a non-standard way...
                        #
                        while True:
                            try:
                                self._outfile.write(data)
                            except IOError:
                                pass
                            else:
                                break
                        self._outfile.flush()
                        if self.options.split_tee:
                            sys.stdout.write(data)
                            sys.stdout.flush()
                        #sys.stdout.write(data)
                        #sys.stdout.flush()
                    else:
                        done = True
            except socket.error, e:
                errmsg = e.strerror.lower()
                self.set_error(errmsg)
                try:
                    sock.close()
                except:
                    pass
                return

        result['addr'] = self._addr
        result['host'] = self._addr[0]
        result['port'] = self._addr[1]
        result['received'] = self._recv_buffer
        result['socket_error'] = socket_error
        return result

    def __format__(self, line, parse_result, action_result):
        output = ''
        if 0:
            if action_result and self.options.verbose:
                output = '{0} {1} {2}'.format(
                    action_result['host'],
                    action_result['port'],
                    action_result['received'],
                )
        host = action_result['addr']
        self.vprint_stderr(1, '[connection closed {0}:{1}]'.format(*host))
        return output

    def __timeout__(self):
        if hasattr(self, '_addr'):
            host, port = self._addr
            return 'timeout {0} {1}\n'.format(host, port)
        return None


def main():
    import xnet.tools.run
    xnet.tools.run.run(NetcatsTool, tool_reads_stdin=True)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
