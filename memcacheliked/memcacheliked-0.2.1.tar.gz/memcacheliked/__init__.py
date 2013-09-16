# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 by Vicious Red Beam
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from functools import wraps
from diesel import Application, Service, Loop, first, until, sleep, send, log
import traceback

STORAGE_STATUS_STORED = 'STORED'
STORAGE_STATUS_NOT_STORED = 'NOT_STORED'
STORAGE_STATUS_EXISTS = 'EXISTS'
STORAGE_STATUS_NOT_FOUND = 'NOT_FOUND'
STORAGE_STATUSES = set([
    STORAGE_STATUS_STORED, STORAGE_STATUS_NOT_STORED, STORAGE_STATUS_EXISTS,
    STORAGE_STATUS_NOT_FOUND])

DELETION_STATUS_DELETED = 'DELETED'
DELETION_STATUS_NOT_FOUND = 'NOT_FOUND'
DELETION_STATUSES = set([DELETION_STATUS_DELETED, DELETION_STATUS_NOT_FOUND])

VALUE_READ_TIMEOUT = 60


class ClientError(Exception):
    pass


class ServerError(Exception):
    pass


class Memcacheliked(object):

    """Abstract memcache interface object

    Inherit this class and implement command_* methods. Each needs
    to be decorated with @{retrieval,storage,deletion}_command to
    verify / process the arguments properly.
    """

    def __init__(self, timeout=60 * 60):
        self.timeout = timeout

    def _connection_handler(self, address):
        try:
            log.info('got incoming connection from <%s>' % (address,))
            while True:
                ev, msg = first(until_eol=True, sleep=self.timeout)
                if ev == 'sleep':
                    log.warn('connection to <%s> timed out' % (address,))
                    break
                else:
                    elements = msg[:-2].split(' ')

                    log.debug('got command parts <%s>' % (elements,))
                    self._command_dispatch(elements[0], elements)

        except Exception as e:
            log.critical('got exception, <%s>' % (traceback.format_exc(),))
            send("SERVER_ERROR internal exception\r\n")

    def _command_dispatch(self, command_name, elements):
        if hasattr(self, 'command_' + command_name):
            try:
                getattr(self, 'command_' + command_name)(*elements)
            except ServerError as e:
                send("SERVER_ERROR %s\r\n" % (e.args[0],))
            except ClientError as e:
                send("CLIENT_ERROR %s\r\n" % (e.args[0],))
            except Exception as e:
                log.critical('got exception, <%s>' % (traceback.format_exc(),))
                send("SERVER_ERROR internal exception\r\n")
        else:
            log.critical('command <%s> unknown' % (command_name,))
            send("ERROR\r\n")

    def start(self, port=11211):
        self.app = Application()
        self.app.add_service(Service(self._connection_handler, port))
        self.app.run()


def ident(*args):
    return args


def _register_command(f, process_result, process_values=ident, min_args=None):
    """Generic helper wrapper for memcache functions"""
    @wraps(f)
    def wrapper(*elements):
        if len(elements) < min_args:
            raise ClientError("not enough parameters (got %s)" % (elements,))

        return process_result(f(*process_values(*elements)))

    return wrapper


def storage_command(f):
    """Decorator for storage commands (set, add, etc.)
    Actual processing function can look like this:

    @storage_command
    def command_set(self, command_name, key, flags, exptime, value, *opts):

    Expected return type: one of STORAGE_STATUS_*
    """

    def process_storage_status(res):
        if res not in STORAGE_STATUSES:
            raise ServerError("internal error")
        else:
            send(res + "\r\n")

    def add_value(*elements):
        ev, msg = first(
            receive=int(elements[5]) + 2, sleep=VALUE_READ_TIMEOUT)
        if ev == 'sleep':
            raise ClientError("reading timed out")
        else:
            new_elements = list(elements)
            new_elements[5] = msg[:-2]
            return tuple(new_elements)

    return _register_command(
        f, process_storage_status, process_values=add_value, min_args=5)


def retrieval_command(f):
    """Decorator for retrieval commands (get...)
    Actual processing function can look like this:

    @retrieval_command
    def command_get(self, command_name, *keys):

    Expected return type: list of (key,flag,value) tuples.
    """

    def format_values(res):
        if not hasattr(res, '__iter__'):
            raise ServerError("internal error")
        else:
            # format each returned value
            for row in res:
                if type(row) != tuple or len(row) < 3:
                    log.crit(
                        "Engine didn't return proper tuple, but "
                        "<%s> - skipping"
                        % (row,))
                elif row[2] is not None:
                    send('VALUE %s %s %i%s\r\n%s\r\n' %
                        (row[0], row[1], len(row[2]), ''
                         if len(row) < 4 else ' ' + row[3], row[2]))
                else:
                    pass
                    # key not present, no answer
            send('END\r\n')

    return _register_command(f, format_values, min_args=2)


def deletion_command(f):
    """Decorator for deletion commands (delete...)
    Actual processing function can look like this:

    @deletion_command
    def command_delete(self, command_name, key, *opts):

    Expected return type: one of DELETION_STATUS_*
    """

    def process_result(res):
        if res not in DELETION_STATUSES:
            raise ServerError("internal error")
        else:
            send(res + "\r\n")
    return _register_command(f, process_result, min_args=2)
