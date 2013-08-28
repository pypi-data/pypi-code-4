# coding: utf-8
from gat_games.game_engine.engine import *

AS = 1
J = 11
Q = 12
K = 13
SPADES = 1
HEARTS = 2
DIAMONDS = 3
CLUBS = 4

class Card(object):
    '''
    Override:
    suit_weights = {...}
    ranks = (...)
    '''
    ranks = (AS, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K)
    suits = (SPADES, HEARTS, DIAMONDS, CLUBS)
    suit_weights = {SPADES: 0, HEARTS: 0, DIAMONDS: 0, CLUBS: 0}
    rank_labels = {AS:'AS', J:'J', Q:'Q', K:'K'}

    # http://en.wikipedia.org/wiki/Suit_(cards)
    def __init__(self, rank, suit, **kwargs):
        if rank not in self.ranks:
            raise AttributeError('Invalid card rank')
        if suit not in self.suits:
            raise AttributeError('Invalid card suit')
        self.rank = rank
        self.suit = suit

    def suit_weight(self):
        return self.suit_weights[self.suit]

    def __lt__(self, other):
        return self.ranks.index(self.rank) < self.ranks.index(other.rank) if other else False

    def __le__(self, other):
        return self.ranks.index(self.rank) <= self.ranks.index(other.rank) if other else False

    def __gt__(self, other):
        return self.ranks.index(self.rank) > self.ranks.index(other.rank) if other else True

    def __ge__(self, other):
        return self.ranks.index(self.rank) >= self.ranks.index(other.rank) if other else True

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit if other else False

    def __ne__(self, other):
        return self.rank != other.rank or self.suit != other.suit if other else True

    def __hash__(self):
        return hash(self.rank) + hash(self.suit)

    def __str__(self):
        return '%s-%s' % (self.rank_labels.get(self.rank, self.rank), self.suit)


class Deck(object):
    '''
    Override:
    Card = CustomCard
    '''
    Card = Card

    def __init__(self):
        self.cards = []

    def __len__(self):
        return self.count()

    def __str__(self):
        return ','.join([str(card) for card in self.cards])

    def getCards(self):
        return self.cards

    def count(self):
        return len(self.cards)

    def clear(self):
        self.cards = []

    def build(self):
        self.clear()
        for suit in self.Card.suits:
            for rank in self.Card.ranks:
                self.cards.append(self.Card(rank, suit))

    def contains(self, card):
        return card in self.cards

    def see(self, index):
        return self.cards[index]

    def push(self, card):
        self.cards.append(card)
        return card

    def pop(self, index=None):
        if index:
            return self.cards.pop(index)
        return self.cards.pop()

    def remove(self, card):
        if card in self.cards:
            self.cards.remove(card)
        return card

    def shuffle(self, random):
        random.shuffle(self.cards)

    def sort(self):
        self.cards.sort()

    def distribute(self, decks, amount):
        for i in range(amount):
            for deck in decks:
                deck.push(self.cards.pop())


class CardGameRound(TurnBasedGame):
    '''
    Override:
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

    Deck = CustomDeck
    def start_round(self): pass
    '''
    Deck = Deck
    StartGameCommand = StartRoundCommand
    EndGameCommand = EndRoundCommand

    def __init__(self, seed, players, **kwargs):
        super(CardGameRound, self).__init__(seed, players, **kwargs)
        self.hands = {}
        for player in self.players:
            self.hands[str(player)] = self.Deck()
        self.new_deck()
        self.start_round()

    def hand(self, player):
        return self.hands[str(player)]

    def new_deck(self):
        self.deck = self.Deck()
        self.deck.build()
        self.deck.shuffle(self.random)

    def start_round(self):
        pass

    def get_context(self, player):
        context = super(CardGameRound, self).get_context(player)
        context['hand'] = self.hands[str(self.player_in_turn)]
        return context

    def distribute_cards_to_each_player(self, amount):
        self.deck.distribute(list(self.hands.values()), amount)


class CardGame(GameComposite):
    '''
    Override:
    Round = CustomRound
    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def play(self): pass
    def before_start_round(self, round_game): pass
    def after_end_round(self, round_game): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()
    '''
    Round = CardGameRound
