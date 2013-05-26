# -*- coding: utf-8 -*-
"""
anigma.core - the brain
"""

import random
import copy
try:
    from multiprocessing import Pool
    MULTI = True
except ImportError:
    MULTI = False

from .util import MAX

import showme


class AI(object):
    def __init__(self, db=None, multi=False, debug=False):
        self.algo = None
        self.heuristic = None
        self.debug = debug
        self.multi = multi
        self.db = db

    def check_compatibility(self, interface):
        pass
        #check algo to game
        #check db to game
        #check heuristic to game, if there not sure

    #@showme.cputime
    def determine(self, game, player):
        if self.algo.values:
            game.values = self.algo.values
        game.init()
        if self.db and game.currentDepth() + 1 < self.db.plyDepth:
            values = self.db_determine(game, player)
        elif self.multi:
            values = self.multi_determine(game, player)
        else:
            values = self.one_determine(game, player)
        a = -MAX
        choices = []
        for move, val in values.iteritems():
            if val > a:
                a = val
                choices = [move]
            elif val == a:
                choices.append(move)
        return random.choice(choices)

    def db_determine(self, game, player):
        values = {}
        for move in game.available_moves():
            game.make_move(move, player)
            val = self.db.simplePositionSearch(copy.deepcopy(game), player)
            game.remove_move(move, player)
            if self.debug:
                print "move", move + 1, ":", val
            values[move] = val
        return values

    def one_determine(self, game, player):
        values = {}
        for move in game.available_moves():
            val = self.sub_determine(game, player, move)
            if self.debug:
                print "move", move + 1, ":", val
            values[move] = val
        return values

    def multi_determine(self, game, player):
        if not MULTI:  # Python 2.5 doesn't support
            return None
        pool = Pool(processes=4)
        moves = game.available_moves()
        subsub = lambda moves: self.sub_determine(game, player, moves)
        scores = pool.map(subsub, moves)
        pool.close()
        pool.join()
        values = dict(zip(moves, scores))
        return values

    def sub_determine(self, game, player, move):
        game.make_move(move, player)
        val = self.algo.run(copy.deepcopy(game), player)
        game.remove_move(move, player)
        return val
