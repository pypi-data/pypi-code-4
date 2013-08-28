# coding: utf-8
# http://rosettacode.org/wiki/Hello_world/Standard_error
# http://en.wikipedia.org/wiki/Inter-process_communication
# http://docs.python.org/2/library/subprocess.html
# http://docs.python.org/3/library/subprocess.html
# http://docs.python.org/2/library/subprocess.html#subprocess.Popen
# http://jimmyg.org/blog/2009/working-with-python-subprocess.html
# http://www.decalage.info/python/ruby_bridge
import logging
import os
import random
from subprocess import Popen
import socket
import sys
import threading
import time

import gat_games.game_engine.gat_json as json
from gat_games.game_engine.engine import Player, GATLogger, AlgorithmError, AlgorithmInitializationError, AlgorithmTimeoutError


def run_with_time_limit(timeout, func, args=(), kwargs={}):
    class FuncThread(threading.Thread):
        def __init__(self):
            super(FuncThread, self).__init__()
            self.result = None

        def run(self):
            self.result = func(*args, **kwargs)

        def stop(self):
            if self.isAlive():
                if hasattr(self, '_Thread__stop'):
                    self._Thread__stop()

    thread = FuncThread()
    thread.start()
    thread.join(timeout)
    if thread.isAlive():
        thread.stop()
        raise AlgorithmTimeoutError('Algorithm timeout error')
    else:
        return thread.result


class GATPlayer(Player):
    DELIMITER = '\n'
    CONNECT_TIMEOUT = 10 # in seconds

    def __init__(self, runtime_command, timeout=1*60, **kwargs):
        super(GATPlayer, self).__init__(**kwargs)
        self.runtime_command = runtime_command
        self.timeout = timeout
        self.algorithm = None
        self.context = None
        self.sock = None
        self.file = None

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict.pop('algorithm', None)
        odict.pop('context', None)
        odict.pop('sock', None)
        odict.pop('conn', None)
        return odict

    def get_valid_port(self, host='localhost'):
        for i in list(range(0, 10)): # avoid infinite loop
            # http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xml
            port = random.randint(1025, 65535)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                result = sock.connect_ex((host, port))
                if result != 0:
                    return port
            finally:
                sock.close()
                time.sleep(0.5)
        return 0

    def start_algorithm_safely(self, runtime_command, player_log=True):
        env = {}
        env_publich_vars = ['PWD', 'PATH', 'HOME', 'TERM', 'SHELL',
            'LOGNAME', 'USER', 'USERNAME', 'SUDO_USER',
            '_',
            'RUBYLIB', 'GEM_PATH', 'GEM_HOME', 'rvm_path', 'rvm_bin_path']
        for var in env_publich_vars:
            value = os.getenv(var, None)
            if value:
                env[var] = value
        # server socket
        if player_log:
            stdout = open('%s.log' % str(self), 'w')
        else:
            stdout = None
        # custom env and stdout/stderr for security
        self.algorithm = Popen(runtime_command, cwd=None, env=env, stdout=stdout, stderr=stdout)
        # self.algorithm.wait() # does not work properly
        time.sleep(1) # giving time to the server start properly

    def start(self, host='localhost', port=None, player_log=False):
        try:
            self.log('Starting algorithm: %s' % self.runtime_command, logging.DEBUG)
            if not port:
                port = self.get_valid_port(host=host)
            self.runtime_command.append(str(port))
            self.runtime_command.append(str(GATLogger.get_log_level()))

            self.start_algorithm_safely(self.runtime_command, player_log=player_log)

            self.log('Algorithm started', logging.DEBUG)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # client socket
            self.sock.settimeout(self.CONNECT_TIMEOUT) # (connection timeout only)
            self.sock.connect((host, port))

            # makefile must use blocking mode
            self.sock.settimeout(None)
            self.sock.setblocking(1)

            self.file = self.sock.makefile("rb") # buffered
            self.log('Algorithm connected', logging.DEBUG)
        except Exception as e:
            self.log(self.runtime_command, logging.ERROR)
            self.log(str(e), logging.ERROR)
            self.stop()
            raise AlgorithmInitializationError(str(e))

    def stop(self):
        if self.sock:
            self.sock.close()
            self.log('Socket closed', logging.DEBUG)
        if self.algorithm:
            self.algorithm.kill()
            self.log('Process killed', logging.DEBUG)

    def send_message_to_algorithm(self, message):
        self.log('>> Sending message to algorithm:\n%s' % message, logging.DEBUG)
        message = '%s%s' % (message, self.DELIMITER)
        if sys.version_info[0] == 2:
            self.sock.sendall(message)
        else:
            self.sock.sendall(bytes(message, 'utf-8'))

    def receive_message_from_algorithm(self):
        self.log('<< Receiving response from algorithm', logging.DEBUG)
        try:
            message = self.file.readline()
            message = message.decode("utf-8") # Python 3
            if message:
                message = message.replace(self.DELIMITER, '')
                message = message.strip()
            self.log('Response: %s' % message, logging.DEBUG)
            return message
        except socket.timeout: # blocking socket will not raise timeout here
            self.log('Timeout %s' % str(self), logging.ERROR)
            raise AlgorithmTimeoutError('Algorithm timeout error: %s' % str(self))

    def delegate_decision_to_the_algorithm(self, message):
        message = json.dumps(message)
        self.send_message_to_algorithm(message)
        response = run_with_time_limit(self.timeout, self.receive_message_from_algorithm)
        if response:
            response = json.loads(response)
            error = response.get('error', None)
            if error:
                raise AlgorithmError('Algorithm error: %s' % error)
            else:
                return self.process_response(response)

    def process_response(self, response):
        return response

    def play(self, context, **kwargs):
        message = {'action':kwargs.get('action', 'play'), 'context':context}
        return self.delegate_decision_to_the_algorithm(message)

