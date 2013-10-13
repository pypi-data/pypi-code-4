#!/usr/bin/env python

from __future__ import print_function

import cmd
import logging

from gevent import monkey

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile


class RemoteControlCmd(cmd.Cmd):

    prompt = 'remote-control> '
    intro = 'Interactive browser remote control\nType "help" for more information.'
    use_rawinput = False

    def __init__(self, server):
        cmd.Cmd.__init__(self)
        self.server = server

    def postcmd(self, stop, line):
        if stop == 'EOF':
            print('^D')
        if stop:
            print('May the maltron be with you!')
            return True

    def do_help(self, args):
        '''Type "help" for the list of available commands and help <command>" for details about a specific command.'''
        cmd.Cmd.do_help(self, args)

    def do_exit(self, args):
        '''Exit the console.'''
        return 'exit'

    def do_eval(self, args):
        '''Call eval() on the browser.'''
        self.server.sessions.notify('eval', args)

    def do_print(self, args):
        '''Call print() on the browser.'''
        self.server.sessions.notify('print', args)

    def do_alert(self, args):
        '''Call alert() on the browser.'''
        self.server.sessions.notify('alert', args)

    def do_EOF(self, args):
        '''You can exit the console by typing Ctrl+D.'''
        return 'EOF'

    def do_who(self, args):
        '''Show connected users'''
        if not self.server.sessions:
            print('No sessions connected.')
            return
        print('%d session%s connected:' % (
            len(self.server.sessions),
            's' if len(self.server.sessions) != 1 else ''))
        print('SESSION ID              IP ADDRESS       TRANSPORT')
        print('--------------------------------------------------')
        #####('xxxxxxxxxxxxxxxxxxxxxx  000.000.000.000  ws/poll  ')
        for session in self.server.sessions:
            print('%-22s  %-15s  %-9s' % (session.id,
                session.transport.remote_addr, session.transport.name))

    def do_gauge(self, args):
        '''Set gauge value'''
        self.server.sessions.notify('gauge', args)


class RemoteControlServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('remote-control.html')),
    ] + ExampleServer.urls

    def __init__(self, listener):
        super(RemoteControlServer, self).__init__(listener, log=None)


if __name__ == '__main__':
    monkey.patch_sys()
    logging.basicConfig(filename='remote-control.log', level=logging.DEBUG)
    listener = (RemoteControlServer.host, RemoteControlServer.port)
    print('Server running at http://%s:%d/' % listener)
    server = RemoteControlServer(listener)
    server.start()
    rccmd = RemoteControlCmd(server)
    rccmd.cmdloop()
    # XXX how to shutdown cleanly?
