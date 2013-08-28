# coding: utf-8
import sys

if sys.version_info[0] == 2:
    from gat_games.games.truco import *
    from gat_games.games.truco_clean_deck import *
else:
    from .truco import *
    from .truco_clean_deck import *

SUPPORTED_GAMES = [Truco, TrucoCleanDeck]
