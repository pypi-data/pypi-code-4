# coding: utf-8
import unittest

from gat_games.game_engine.cardgame import *
from gat_games.games.truco import *


class TrucoPlayerTests(unittest.TestCase):
    def test_gat_player_must_be_serializable(self):
        result = json.dumps(TrucoPlayer(['python',  'x']))
        self.assertEquals('{}', result)


class TrucoCardTests(unittest.TestCase):
    def test_rank_order(self):
        self.assertEquals(True, TrucoCard(AS, SPADES) > TrucoCard(K, SPADES))
        self.assertEquals(True, TrucoCard(3, SPADES) > TrucoCard(AS, SPADES))
        self.assertEquals(True, TrucoCard(3, SPADES) > TrucoCard(K, SPADES))
        self.assertEquals(True, TrucoCard(3, SPADES) > TrucoCard(7, SPADES))

        self.assertEquals(True, TrucoCard(4, SPADES) < TrucoCard(2, SPADES))
        self.assertEquals(True, TrucoCard(4, SPADES) < TrucoCard(AS, SPADES))
        self.assertEquals(True, TrucoCard(4, SPADES) < TrucoCard(Q, SPADES))

    def test_manilha(self):
        self.assertEquals(True, TrucoCard(2, SPADES).is_manilha(TrucoCard(AS, SPADES)))
        self.assertEquals(True, TrucoCard(3, SPADES).is_manilha(TrucoCard(2, SPADES)))
        self.assertEquals(True, TrucoCard(AS, SPADES).is_manilha(TrucoCard(K, SPADES)))
        self.assertEquals(True, TrucoCard(K, SPADES).is_manilha(TrucoCard(J, SPADES)))
        self.assertEquals(True, TrucoCard(J, SPADES).is_manilha(TrucoCard(Q, SPADES)))
        self.assertEquals(True, TrucoCard(Q, SPADES).is_manilha(TrucoCard(7, SPADES)))
        self.assertEquals(True, TrucoCard(4, SPADES).is_manilha(TrucoCard(3, SPADES)))

        self.assertEquals(False, TrucoCard(2, SPADES).is_manilha(TrucoCard(2, SPADES)))
        self.assertEquals(False, TrucoCard(3, SPADES).is_manilha(TrucoCard(AS, SPADES)))


class TrucoDeckTests(unittest.TestCase):
    def test_build(self):
        deck = TrucoDeck()
        deck.build()
        self.assertEquals(10*4, len(deck))


class TrucoRoundTests(unittest.TestCase):
    def setUp(self):
        self.p1 = TrucoPlayer()
        self.p2 = TrucoPlayer()
        self.truco = TrucoRound(0, [self.p1, self.p2])
        self.truco.start_new_cycle()
        self.truco.player_in_turn = self.p1

    def test_truco_context(self):
        context = self.truco.get_context(self.truco.player_in_turn)
        print(context)
        # self.assertEquals(1, context['game_number'])
        self.assertEquals(self.truco.hands[self.truco.player_in_turn.name], context['hand'])
        self.assertEquals(self.truco.value, context['round_value'])
        self.assertEquals(self.truco.truco_value, context['round_truco_value'])
        self.assertEquals(self.truco.center_card, context['round_center_card'])
        self.assertEquals(self.truco.table, context['round_table'])

    def test_start_distribute_3_cards_to_each_player(self):
        self.assertEquals(3, len(self.truco.hands[self.p1.name]))
        self.assertEquals(3, len(self.truco.hands[self.p2.name]))

    def test_truco_next_player(self):
        self.assertEquals(self.p2, self.truco.next_player())
        self.truco.player_in_turn = self.truco.next_player()
        self.assertEquals(self.p1, self.truco.next_player())

    def test_upcard(self):
        card = self.truco.hand(self.truco.player_in_turn).see(0)
        self.truco.player_in_turn.upcard(card)
        self.assertEquals(1, len(self.truco.table))
        self.assertEquals(2, self.truco.hands[self.truco.player_in_turn.name].count())

    def test_winning_card_without_manilha(self):
        card = self.truco.winning_card([TrucoCard(4, SPADES), TrucoCard(3, SPADES)], TrucoCard(AS, SPADES))
        self.assertEquals(TrucoCard(3, SPADES), card)

    def test_winning_card_with_one_manilha(self):
        card = self.truco.winning_card([TrucoCard(3, SPADES), TrucoCard(AS, SPADES)], TrucoCard(K, SPADES))
        self.assertEquals(TrucoCard(AS, SPADES), card)

    def test_winning_card_with_many_manilhas(self):
        card = self.truco.winning_card([TrucoCard(AS, CLUBS), TrucoCard(AS, SPADES)], TrucoCard(K, SPADES))
        self.assertEquals(TrucoCard(AS, CLUBS), card)

    def test_p1_wins(self):
        pass

    def test_draw(self):
        pass


class DefaultPlayer(TrucoPlayer):
    def has_accepted_truco(self, context):
        return True

    def upcard_or_truco(self, context):
        self.upcard(context['hand'].see(0))


class AgressivePlayer(TrucoPlayer):
    def has_accepted_truco(self, context):
        return True

    def upcard_or_truco(self, context):
        if self.can_truco(context):
            self.truco()
        else:
            self.upcard(context['hand'].see(0))


class DefensivePlayer(TrucoPlayer):
    def has_accepted_truco(self, context):
        return False

    def upcard_or_truco(self, context):
        self.upcard(context['hand'].see(0))


class BuggedPlayer(TrucoPlayer):
    def has_accepted_truco(self, context):
        return True

    def upcard_or_truco(self, context):
        self.truco()


class TrucoRoundPlayingTests(unittest.TestCase):
    def test_round_without_truco(self):
        self.p1 = DefaultPlayer()
        self.p2 = DefaultPlayer()
        self.truco = TrucoRound(0, [self.p1, self.p2])
        self.truco.start()
        self.assertEquals(None, self.truco.error)

    def test_round_with_accepted_truco(self):
        self.p1 = AgressivePlayer()
        self.p2 = DefensivePlayer()
        self.truco = TrucoRound(0, [self.p1, self.p2])
        self.truco.start()
        self.assertEquals(None, self.truco.error)

    def test_round_with_gived_up_truco(self):
        self.p1 = DefensivePlayer()
        self.p2 = DefensivePlayer()
        self.truco = TrucoRound(0, [self.p1, self.p2])
        self.truco.start()
        self.assertEquals(None, self.truco.error)

    def test_round_only_with_truco(self):
        self.p1 = AgressivePlayer()
        self.p2 = AgressivePlayer()
        self.truco = TrucoRound(0, [self.p1, self.p2])
        self.truco.start()
        self.assertEquals(None, self.truco.error)

    def test_bugged_algorithms(self):
        self.p1 = BuggedPlayer()
        self.p2 = BuggedPlayer()
        self.truco = TrucoRound(0, [self.p1, self.p2])
        self.truco.start()
        self.assertEquals('RE', self.truco.error)


class TrucoTests(unittest.TestCase):
    def test_truco_empty_context(self):
        truco = Truco(0, [])
        self.assertEquals({}, truco.scoreboard)

    def test_truco_context(self):
        truco = Truco(0, [TrucoPlayer(), TrucoPlayer()])
        self.assertEquals([0, 0], list(truco.scoreboard.values()))

    def test_round_summary_is_propagated_to_game_summary_in_case_of_error(self):
        truco = Truco(0, [BuggedPlayer(), BuggedPlayer()])
        truco.start()
        self.assertEquals('RE', truco.error)
        self.assertEquals('You can not truco until another player re-truco', truco.error_message)

