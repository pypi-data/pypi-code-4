import errno
import logging
import os
import select
import socket
import sys


log = logging.getLogger(__name__)


REQUEST_QUEUE_SIZE = 5


class TCPServer(object):

    def __init__(self, q, host='localhost', port=9999):
        self.q = q
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(REQUEST_QUEUE_SIZE)

    def process_request(self, request, client_address):
        rfile = request.makefile('rb', -1)

        try:
            while True:
                data = rfile.readline().strip()
                if not data:
                    break
                log.info("%r wrote: %r", client_address[0], data)

                self.q.put(data)
        finally:
            rfile.close()

        request.close()

    def wait_and_handle(self, poll_interval):
        def _eintr_retry(func, *args):
            """restart a system call interrupted by EINTR"""
            while True:
                try:
                    return func(*args)
                except (OSError, select.error) as e:
                    if e.args[0] != errno.EINTR:
                        raise

        # XXX: Consider using another file descriptor or
        # connecting to the socket to wake this up instead of
        # polling. Polling reduces our responsiveness to a
        # shutdown request and wastes cpu at all other times.

        # r, w, e = _eintr_retry(select.select, [self.socket], [], [],
        #                        poll_interval)
        r, w, e = select.select([self.socket], [], [], poll_interval)
        if self.socket not in r:
            return

        try:
            request, client_address = self.socket.accept()
        except socket.error:
            return

        try:
            self.process_request(request, client_address)
        except Exception:
            log.error("Socket request error: %r %r", request, client_address)
            request.close()
