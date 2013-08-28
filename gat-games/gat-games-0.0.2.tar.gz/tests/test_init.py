# coding: utf-8
import re

import unittest


class InitTests(unittest.TestCase):
    def test_version(self):
        from gat_games import VERSION
        print(re.match(r'\d[.]\d[.]\d', VERSION))
        self.assertEquals(True, bool(re.match(r'\d[.]\d[.]\d', VERSION)))

    def test_game_import_shortcut(self):
        from gat_games.games import SUPPORTED_GAMES, Truco
        from gat_games.games.truco import Truco
