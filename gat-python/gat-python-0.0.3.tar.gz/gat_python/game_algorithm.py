# coding: utf-8
from functools import update_wrapper
import logging
import socket
import sys

import six


try:
    import simplejson as json
except ImportError:
    import json


def encode_object(obj):
    if hasattr(obj, '__getstate__'):
        return obj.__getstate__
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return obj


def dumps(obj, **kwargs):
    return json.dumps(obj, skipkeys=True, default=encode_object, **kwargs)


def loads(s, **kwargs):
    return json.loads(s, **kwargs)


class GameAlgorithm(object):
    '''
    Usage:

    import os
    import sys
    sys.path.append(os.getcwd())
    algorithm = GameAlgorithm()
    algorithm.listen()
    '''
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.file = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_log()

    def config_log(self):
        FORMAT = '%(message)s'
        logging.basicConfig(format=FORMAT)
        log_level = int(sys.argv[2]) if len(sys.argv) > 2 else logging.INFO
        self.logger.setLevel(log_level)

    def log(self, message, level=logging.INFO):
        if self.logger:
            self.logger.log(level, '[GATPython] %s' % (message,))

    def listen(self, host='localhost', port=None):
        if not port:
            port = int(sys.argv[1]) if len(sys.argv) > 1 else 58888
        self.sock.bind((host, port))
        self.log('Listening %s' % str((host, port)), logging.DEBUG)
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        self.file = self.conn.makefile("rb") # buffered
        self.log('Client connected: %s' % str(addr), logging.DEBUG)

        self.stopped = False
        while not self.stopped:
            try:
                self.read_incoming_message()
            except Exception as e:
                self.log(str(e), logging.ERROR)
                self.send_error(str(e))
                self.stop()
                self.close()
                six.reraise(*sys.exc_info())
        self.close()

    def stop(self):
        self.stopped = True

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.sock:
            self.sock.close()
            self.sock = None

    def read_incoming_message(self):
        message = self.file.readline()
        if message:
            message = message.strip()
        if not message or message == 'stop':
            self.stop()
        else:
            message = loads(message)
            self.process_message(message)

    def process_message(self, message):
        if message['action'] == 'play':
            return self.play(message['context'])

    def play(self, context):
        pass

    def send_response(self, message):
        message = dumps(message)
        message = '%s\n' % message
        if sys.version_info[0] == 2:
            self.conn.sendall(message)
        else:
            self.conn.sendall(bytes(message, 'utf-8'))

    def send_error(self, error_message):
        error = {'error': error_message}
        self.send_response(error)
