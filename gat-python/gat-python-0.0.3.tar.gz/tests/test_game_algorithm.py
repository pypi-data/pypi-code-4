# coding: utf-8
import os
import random
import socket
from subprocess import Popen
import sys
import time

import unittest


full_path = os.path.realpath(__file__)
dirpath, filename = os.path.split(full_path)


def get_valid_port(host='localhost'):
    while True:
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


class IPCTests(unittest.TestCase):
    def algorithm_file(self):
        pass

    def setUp(self):
        filepath = os.path.join(dirpath, 'sample_algorithms', self.algorithm_file())
        port = get_valid_port()
        self.proc = Popen(['python', filepath, str(port)])
        time.sleep(1)
        print(filepath, self.proc.poll(), self.proc.pid)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3) # in seconds
        self.sock.connect(('localhost', port))

    def tearDown(self):
        self.sock.close()
        self.proc.kill()


class CorrectGameAlgorithmTests(IPCTests):
    def algorithm_file(self):
        return 'correct_game_algorithm.py'

    def test_send_and_receive_messages_through_ipc(self):
        if sys.version_info[0] == 2:
            self.sock.sendall('"msg x"\n')
        else:
            self.sock.sendall(bytes('"msg x"\n', 'utf-8'))
        response = self.sock.makefile().readline()
        self.assertEquals('"echo: msg x"\n', response)


class BuggedGameAlgorithmTests(IPCTests):
    def algorithm_file(self):
        return 'bugged_game_algorithm.py'

    def test_send_and_receive_messages_through_ipc(self):
        if sys.version_info[0] == 2:
            self.sock.sendall('"msg x"\n')
        else:
            self.sock.sendall(bytes('"msg x"\n', 'utf-8'))
        response = self.sock.makefile().readline()
        self.assertEquals('{"error": "runtime error"}\n', response)
