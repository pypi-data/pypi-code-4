# coding: utf-8
import sys

if sys.version_info[0] == 2:
    from gat_runner.players.truco import *
else:
    from .truco import *

