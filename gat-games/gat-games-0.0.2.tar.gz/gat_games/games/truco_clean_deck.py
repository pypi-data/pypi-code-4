# coding: utf-8
from gat_games.games.truco import *


class TrucoCleanDeckCard(TrucoCard):
    ranks = (Q, J, K, AS, 2, 3)


class TrucoCleanDeckDeck(TrucoDeck):
    Card = TrucoCleanDeckCard


class TrucoCleanDeckRound(TrucoRound):
    Deck = TrucoCleanDeckDeck


class TrucoCleanDeck(Truco):
    Round = TrucoCleanDeckRound


class RandomTrucoCleanDeckPlayer(RandomTrucoPlayer):
    pass

