# coding: utf-8
import os
import tempfile
import unittest
from nose.tools import raises

import gat_games.game_engine.gat_json as json
from gat_games.game_engine.engine import *
from gat_runner.players.gat_player import *


class StubGATPlayer(GATPlayer):
    def play(self, context, **kwargs):
        self.worked = False
        self.response = super(StubGATPlayer, self).play(context, **kwargs)
        self.worked = True
        return self.response


class GATPlayerTests(unittest.TestCase):
    def test_gat_player_must_be_serializable(self):
        result = json.dumps(StubGATPlayer(['python',  'x']))
        self.assertEquals('{}', result)

    def execute_algorithm(self, code, response):
        f, filepath = tempfile.mkstemp(text=True)
        f = open(filepath, 'w')
        f.write(code)
        f.close()
        player = StubGATPlayer(['python',  filepath], timeout=1)
        try:
            player.start()
            player.play({}) # send message to the algorithm
            self.assertEquals(True, player.worked)
            self.assertEquals(response, player.response)
        finally:
            player.stop()
            os.remove(filepath)

    def test_correct_algorithm(self):
        code = '''
print('Running Correct Algorithm')
import socket
import sys
print('[1] Args: ' + str(sys.argv))
port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', port))
sock.listen(1)
conn, addr = sock.accept()

print('[1] Algorithm waiting for message')
message = conn.recv(8192)

print('[1] Algorithm sending message')
conn.sendall(message)
print('[1] Message sent')
'''
        self.execute_algorithm(code, {u'action': u'play', u'context': {}})

    @raises(AlgorithmTimeoutError)
    def test_slow_algorithm(self):
        code = '''
print('Running Slow Algorithm')
import socket
import sys
print('[2] Args: ' + str(sys.argv))
port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', port))
sock.listen(1)
conn, addr = sock.accept()

import time
time.sleep(2)
'''
        self.execute_algorithm(code, None)

    @raises(AlgorithmError)
    def test_bugged_algorithm(self):
        code = '''
print('Running Bugged Algorithm')
import socket
import sys
print('[3] Args: ' + str(sys.argv))
port = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', port))
sock.listen(1)
conn, addr = sock.accept()

print('[3] Algorithm waiting for message')
message = conn.recv(8192)

print('[3] Algorithm sending message')
error = '{"error":"exception message"}'
if sys.version_info[0] == 2:
    conn.sendall(error)
else:
    conn.sendall(bytes(error, 'utf-8'))
print('[3] Message sent')
'''
        self.execute_algorithm(code, None)

    @raises(AlgorithmInitializationError)
    def test_bugged_algorithm_in_the_initialization(self):
        code = '''
print('Running Bugged Algorithm')
raise Exception('ops')
'''
        self.execute_algorithm(code, None)
