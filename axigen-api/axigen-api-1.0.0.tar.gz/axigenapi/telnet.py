#!/usr/bin/env python

'''
Telnet module
'''

from axigenapi import connection as nsock


class client(nsock.connection):
    '''
    Telnet connection class
    '''

    def send(self, data):
        '''
        Send data through socket
            :param str data: Data to be sent
            :return: bool
        '''
        status = self._send(data)
        return(status)

    def receive(self, shot_receive=False):
        '''
        Receieve data through socket
            :param bool shot_receive: Should we do one-hit receive,
                not waiting for all data to come to us?
            :return: str
        '''
        data = None
        if (shot_receive is True):
            data = self._receive_once()
        else:
            data = self._receive()
        return(data)

    def _send_command(self, command, delimiter="\n", shot_receive=True):
        '''
        Appends delimiter to the telnet command and then submits it to the
        telnet service. Then it retrieves answer from the telnet service
        and return it back to the caller.
            :param str command: Command to be sent
            :param str delimiter: Delimit the command at the end with...
            :param bool shot_receive: Should we do one-hit receive,
                not waiting for all data to come to us?
            :return: str
        '''
        command = str(command).strip()
        if (command == ''):
            return(False)
        command += delimiter
        status = self.send(command)
        returnvalue = None
        if (status):
            returnvalue = None
            returnvalue = self.receive(shot_receive)
        return(returnvalue)
