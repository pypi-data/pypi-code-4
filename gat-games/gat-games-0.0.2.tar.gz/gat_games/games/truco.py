# coding: utf-8
import random

from gat_games.game_engine.engine import *
from gat_games.game_engine.cardgame import *

# TODOs:
# who wins start next round => must_start_new_cycle BUG?


class TrucoPlayer(Player):
    def play(self, context, **kwargs):
        if kwargs.get('action', 'play') == 'accept_truco':
            if self.has_accepted_truco(context):
                self.accept_truco()
            else:
                self.reject_truco()
        else:
            self.upcard_or_truco(context)

    def has_accepted_truco(self, context): pass

    def upcard_or_truco(self, context): pass

    def can_truco(self, context):
        return context['round_can_truco']

    def upcard(self, card):
        self.game.execute_command(Upcard(self, card=card))

    def truco(self):
        self.game.execute_command(TrucoCommand(self))

    def accept_truco(self):
        self.game.execute_command(AcceptTruco(self))

    def reject_truco(self):
        self.game.execute_command(RejectTruco(self))


class RandomTrucoPlayer(TrucoPlayer):
    def has_accepted_truco(self, context):
        return bool(random.randint(0, 1))

    def upcard_or_truco(self, context):
        option = random.randint(0, 10)
        if self.can_truco(context) and option > 5:
            self.truco()
        else:
            hand = context['hand']
            random_index = random.randint(0, len(hand)-1)
            random_card = hand.see(random_index)
            self.upcard(random_card)


class TrucoCard(Card):
    suit_weights = {SPADES: 2, HEARTS: 3, DIAMONDS: 1, CLUBS: 4}
    ranks = (4, 5, 6, 7, Q, J, K, AS, 2, 3)
    # ranks = (Q, J, K, AS, 2, 3)

    def is_manilha(self, center_card):
        i1 = self.ranks.index(self.rank)
        i2 = self.ranks.index(center_card.rank)
        return i1 == i2 + 1 or (i2 == len(self.ranks) - 1 and i1 == 0)


class TrucoDeck(Deck):
    Card = TrucoCard


def get_key_by_value(the_dict, value):
    index = list(the_dict.values()).index(value)
    key = list(the_dict.keys())[index]
    return key


class Upcard(PlayerGameCommand):
    def validate(self, game, context):
        card = self.kwargs.get('card')
        if game.player_in_turn != self.player:
            raise InvalidCommandError('Player can not upcard right now')
        if not game.hand(self.player).contains(card):
            raise InvalidCommandError('Invalid card to upcard')
        if game.state != 'playing':
            raise InvalidCommandError('Need to accept/reject Truco before upcard')

    def execute(self, game):
        card = self.kwargs.get('card')
        card = game.hand(self.player).remove(card)
        game.table[str(self.player)] = card


class TrucoCommand(PlayerGameCommand):
    def validate(self, game, context):
        if game.player_in_turn != self.player and game.next_player() != self.player:
            raise InvalidCommandError('It is not your resposibility to Truco right now')
        if game.last_player_who_truco == self.player:
            raise InvalidCommandError('You can not truco until another player re-truco')
        if game.value >= 12:
            raise InvalidCommandError('Game has already been setted to all-in')
        if game.truco_value >= 12:
            raise InvalidCommandError('Game has already been setted to all-in')

    def execute(self, game):
        if game.value == 1:
            game.truco_value = 3
        else:
            game.truco_value = game.value + 3
        game.last_player_who_truco = self.player
        game.state = 'truco'


class AcceptTruco(PlayerGameCommand):
    def validate(self, game, context):
        if game.last_player_who_truco == self.player:
            raise InvalidCommandError('You can not accept your own Truco')
        if game.state != 'truco':
            raise InvalidCommandError('No truco to accept')

    def execute(self, game):
        game.value = game.truco_value
        game.truco_value = 0
        game.state = 'playing'


class RejectTruco(PlayerGameCommand):
    def validate(self, game, context):
        if game.last_player_who_truco == self.player:
            raise InvalidCommandError('You can not reject your own Truco')
        if game.state != 'truco':
            raise InvalidCommandError('No truco to reject')

    def execute(self, game):
        self.truco_rejected = True
        game.wins[str(game.player_in_turn)] = 3
        game.state = 'playing'
        raise EndGame()


class StartRoundCommand(StartRoundCommand):
    def read_context(self, game):
        self.kwargs['center_card'] = game.center_card
        for player in game.players:
            self.kwargs[str(player)] = game.hand(player).getCards()


class TrucoRound(CardGameRound):
    Deck = TrucoDeck
    StartGameCommand = StartRoundCommand

    def prepare(self): pass

    def start_round(self):
        self.truco_rejected = False
        self.wins = {}
        for player in self.players:
            self.wins[str(player)] = 0
        self.value = 1 # accepted truco update round value
        self.truco_value = 0
        self.last_player_who_truco = None
        self.center_card = self.deck.pop()

        self.new_deck()
        self.distribute_cards_to_each_player(3)
        self.table = {}
        self.state = 'playing'

    def get_context(self, player):
        context = super(TrucoRound, self).get_context(player)
        context['round_value'] = self.value
        context['round_truco_value'] = self.truco_value
        context['round_center_card'] = self.center_card
        context['round_table'] = self.table
        context['round_wins'] = self.wins
        context['round_state'] = self.state
        context['round_can_truco'] = self.player_in_turn != self.last_player_who_truco and self.value < 12 and self.truco_value < 12
        return context

    def before_play(self): pass

    def must_start_new_cycle(self):
        return len(self.table) == len(self.players)

    def start_new_cycle(self):
        self.table = {}
        # FIXME player_in_turn = self.winner_last_cycle

    def before_player_play(self, player, context): pass

    def play(self):
        if self.must_start_new_cycle():
            self.start_new_cycle()
        self.player_in_turn = self.next_player()
        if self.state == 'truco':
            self.player_play(self.player_in_turn, action='accept_truco')
        else:
            self.player_play(self.player_in_turn)

    def after_player_play(self, player, context, response=None):
        if len(self.table) == len(self.players):
            cards = list(self.table.values())
            winning_card = self.winning_card(cards, self.center_card)
            indexes = [i for i, x in enumerate(list(self.table.values())) if x == winning_card] # can have a draw
            # draw count one win for each player
            for index in indexes:
                winner = list(self.table.keys())[index]
                self.wins[winner] += 1

    def after_play(self): pass

    def is_the_end(self):
        # draw count one win for each player
        return max(self.wins.values()) >= 2 or self.truco_rejected

    def the_end(self):
        winner_wins = max(self.wins.values())
        loser_wins = min(self.wins.values())
        self.winners = [get_key_by_value(self.wins, winner_wins)]
        self.losers = [get_key_by_value(self.wins, loser_wins)]

    def summary(self):
        s = super(TrucoRound, self).summary()
        s.update({
            'round_value': self.value,
            'wins': self.wins,
        })
        return s

    # Auxiliar methods

    def winning_card(self, cards, center_card):
        manilhas = []
        for card in cards:
            if card.is_manilha(center_card):
                manilhas.append(card)
        if manilhas:
            manilhas = sorted(manilhas, key=lambda card: card.suit_weight())
            return manilhas[-1]
        else:
            return max(cards)


class Truco(CardGame):
    Round = TrucoRound
    RandomStrategy = RandomTrucoPlayer
    Player = TrucoPlayer

    def __init__(self, seed, players, **kwargs):
        super(Truco, self).__init__(seed, players, **kwargs)
        self.scoreboard = {}
        for player in self.players:
            self.scoreboard[str(player)] = 0

    def prepare(self): pass

    def get_context(self, player):
        return super(Truco, self).get_context(player)

    def before_play(self): pass
    def before_start_round(self, round_game): pass

    def after_end_round(self, round_game):
        for winner in round_game.winners:
            self.scoreboard[str(winner)] += round_game.value

    def after_play(self): pass

    def is_the_end(self):
        return max(self.scoreboard.values()) >= 12

    def the_end(self):
        index_winner = max(self.scoreboard.values())
        index_loser = min(self.scoreboard.values())
        self.winners = [get_key_by_value(self.scoreboard, index_winner)]
        self.losers = [get_key_by_value(self.scoreboard, index_loser)]

    def summary(self):
        s = super(Truco, self).summary()
        s.update({
          'scoreboard': self.scoreboard
        })
        return s
