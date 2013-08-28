# coding: utf-8
from gat_games.game_engine.engine import *
from gat_games.game_engine.cardgame import *
from gat_games.games.truco import *
from gat_runner.players.gat_player import GATPlayer


class TrucoGATPlayer(GATPlayer):
    def process_response(self, response):
        if response['action'] == 'upcard':
            card = TrucoCard(response['hand_card']['rank'], response['hand_card']['suit'])
            self.upcard(card)
        elif response['action'] == 'truco':
            self.truco()
        elif response['action'] == 'accept_truco':
            self.accept_truco()
        elif response['action'] == 'giveup_truco':
            self.reject_truco()
        else:
            raise InvalidCommandError('Invalid action: %s' % response['action'])

    def upcard(self, card):
        self.game.execute_command(Upcard(self, card=card))

    def truco(self):
        self.game.execute_command(TrucoCommand(self))

    def accept_truco(self):
        self.game.execute_command(AcceptTruco(self))

    def reject_truco(self):
        self.game.execute_command(RejectTruco(self))


Truco.Player = TrucoGATPlayer