# coding: utf-8
import unittest

from gat_python.truco_algorithm import *


class StubTrucoAlgorithm(TrucoAlgorithm):
    def __init__(self):
        self.execute_play_method = False
        self.execute_accept_method = False

    def play(self, context):
        self.execute_play_method = True

    def accept_truco(self, context):
        self.execute_accept_method = True

    def send_response(self, message):
        pass


class TrucoAlgorithmTests(unittest.TestCase):
    def test_play_message(self):
        algorithm = StubTrucoAlgorithm()
        algorithm.process_message({'action': 'play', 'context':{}})
        self.assertEquals(True, algorithm.execute_play_method)
        self.assertEquals(False, algorithm.execute_accept_method)

    def test_accept_or_giveup_truco_message(self):
        algorithm = StubTrucoAlgorithm()
        algorithm.process_message({'action': 'accept_truco', 'context':{}})
        self.assertEquals(False, algorithm.execute_play_method)
        self.assertEquals(True, algorithm.execute_accept_method)
