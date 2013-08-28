# coding: utf-8
import os
import unittest

from nose.tools import raises

from gat_games import *
from gat_runner.runner import *


class PlayGatTests(unittest.TestCase):
    def test_play_with_native_python_players(self):
        game = play_gat(Truco, 1, [RandomTrucoPlayer(), RandomTrucoPlayer()])
        report = game.summary()
        self.assertEquals(None, report['error'])
        self.assertEquals(True, report['scoreboard'][report['winners'][0]] >= 12)


class PlayNativePlayerAgainstRandomAlgorithmTests(unittest.TestCase):
    def test_play_native_algorithm_vs_random_algorithm(self):
        play_native_algorithm_vs_random_algorithm(Truco, 1, RandomTrucoPlayer())


class PlayFileAgainstRandomAlgorithmTests(unittest.TestCase):
    def test_play_file_against_random_algorithm(self):
        full_path = os.path.realpath(__file__)
        dirpath, filename = os.path.split(full_path)
        filepath = os.path.join(dirpath, 'sample_truco_algorithm.py')
        print(filepath)
        play_file_against_random_algorithm(Truco, 1, filepath)


class PlayFileAgainstFileTests(unittest.TestCase):
    def test_play_file_against_file(self):
        full_path = os.path.realpath(__file__)
        dirpath, filename = os.path.split(full_path)
        filepath = os.path.join(dirpath, 'sample_truco_algorithm.py')
        print(filepath)
        play_file_against_file(Truco, 1, filepath, filepath)

