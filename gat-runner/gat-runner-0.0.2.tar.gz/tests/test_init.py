# coding: utf-8
import re

import unittest


class InitTests(unittest.TestCase):
    def test_version(self):
        from gat_runner import VERSION
        print(re.match(r'\d[.]\d[.]\d', VERSION))
        self.assertEquals(True, bool(re.match(r'\d[.]\d[.]\d', VERSION)))

    def test_game_import_shortcut(self):
        from gat_runner.players import TrucoGATPlayer
        from gat_runner.players.truco import TrucoGATPlayer
