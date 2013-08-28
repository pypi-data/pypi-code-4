# coding: utf-8
import random

from gat_games.game_engine.engine import *
from gat_games.game_engine.cardgame import *


class XPlayer(Player):
    def play(self, context, **kwargs):
        pass


class RandomXPlayer(XPlayer):
    def play(self, context, **kwargs):
        option = random.randint(0, 10)


class XCard(Card):
    suit_weights = {SPADES: 2, HEARTS: 3, DIAMONDS: 1, CLUBS: 4}
    ranks = (4, 5, 6, 7, Q, J, K, AS, 2, 3)


class XDeck(Deck):
    Card = XCard


class XRound(CardGameRound):
    Deck = XDeck

    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def start_new_cycle(self): pass
    def before_player_play(self, player, context): pass
    def after_player_play(self, player, context, response=None): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()


class X(CardGame):
    Round = XRound

    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def start_new_cycle(self): pass
    def before_player_play(self, player, context): pass
    def after_player_play(self, player, context, response=None): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()
