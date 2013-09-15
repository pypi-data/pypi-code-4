#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2011 Krister Hedfors
#
# FIXME:
#   -x -y -O is much slower than only -x -y
#
#   network-is-unreachable goes stdout
#

__all__ = ['TcpStateTool']


import socket

from xnet.tools import Tool
from xnet.tools import ToolMixin_AddrIterator
from xnet.tools import WaitTimeout
from xnet.debug import pdb


class TcpStateTool(ToolMixin_AddrIterator, Tool):
    '''
        TcpStateTool
            Default format is:
                {addr} {port} {state}
            Output is sent to stderr when state
            is neither 'open', 'closed' nor 'filtered',
            (such as address resolution errors).
    '''

    __toolname__ = 'tcpstate'
    __itemname__ = 'host'
    __description__ = 'test if TCP-ports are open'

    DEFAULT_PORT = 80

    cmdline_options = [
        ('-p', '--port', 'port to state check',
            dict(dest='port')),
        ('-O', '--open', 'only print open ports',
            dict(dest='open', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __repr__(self):
        state = ('x', 'finished')[self.finished]
        if hasattr(self, '_addr'):
            host, port = self._addr
            return '<tcpstate {0}:{1} {2}>'.format(host, port, state)
        return '<tcpstate {0}>'.format(state)

    def __action__(self, parse_result):
        addr = parse_result['addr']
        state = None
        result = {}
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(addr)
            state = 'open'
        except WaitTimeout:
            raise
        except socket.error, e:
            #
            # errno numbers differ between platforms,
            # but tests for 'closed' and 'filtered'
            # below should work universally.
            #
            errmsg = e.strerror.lower()
            if 'connection refused' in errmsg:
                state = 'closed'
            elif 'timed out' in errmsg:
                state = 'filtered'
            else:
                state = errmsg.replace(' ', '-').replace(',', '-')
                self.set_error(state, 1)
                return
        #except gevent.GreenletExit:
        #    #
        #    # happens in BT, not OSX
        #    #
        #    state = 'filtered'
        finally:
            if s:
                s.close()
        result['host'] = addr[0]
        result['port'] = addr[1]
        result['state'] = state
        return result

    def __filter__(self, action_result):
        if self.options.open:
            return action_result and action_result['state'] == 'open'
        return action_result

    def __format__(self, line, parse_result, action_result):
        output = ''
        if action_result:
            if self.options.open:
                output = '{0} {1}'.format(
                    action_result['host'],
                    action_result['port'],
                )
            else:
                output = '{0} {1} {2}'.format(
                    action_result['host'],
                    action_result['port'],
                    action_result['state'],
                )
        return output

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 host    - target host
 port    - target port
 state   - TCP-state or error-message
 time    - time consumed by action, in ms
 pid     - PID of executing process
 grid    - Greenlet ID of executing process

Default format:
 '{host} {port} {state}'
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        if hasattr(self, '_addr'):
            host, port = self._addr
            return '{0} {1} wait-timeout\n'.format(host, port)
        return None


def main():
    import xnet.tools.run
    xnet.tools.run.run(TcpStateTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
