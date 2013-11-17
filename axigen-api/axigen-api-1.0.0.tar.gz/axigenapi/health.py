#!/usr/bin/env

from axigenapi import api
from axigen.connection import ConnectionError as CErr, SocketError as SErr


class checks(object):
    '''
    Service Healthckecks class
    '''

    __axigen = None
    __errors = {}

    def check_axigen(self, hostname='localhost', port=7000):
        '''
        Axigen service health checker
        '''
        status = None
        try:
            conn = api.api(hostname, port)
            self.__axigen = conn
        except (SErr, CErr), message:
            self.__errors['axigen'] = str(message)
            return(False)
        status = self.__axigen.get_version()
        if (status is False):
            self.__errors['axigen'] = \
                "Couldn't pull verification version info from" \
                "Axigen service"
            return(False)
        # All seems fine with Axigen service. Shall we introduce
        # more detailed returned version value check here?
        return(True)

    def get_errors(self, service=None):
        '''
        Returns error(s) for all (if service not defined) or just for
        one service.
        '''
        errors = None
        if (service is not None):
            try:
                errors = self.__errors[service]
            except KeyError:
                errors = None
        else:
            errors = self.__errors
        return(errors)
