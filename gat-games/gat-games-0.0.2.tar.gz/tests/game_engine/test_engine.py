# coding: utf-8
import unittest
from nose.tools import raises

from gat_games.game_engine.engine import *


class PlayerTests(unittest.TestCase):
    def test_default_name_is_the_class_name_with_the_id(self):
        player = Player()
        self.assertEquals(True, player.name.startswith('Player'))

    def test_custom_name(self):
        player = Player('me')
        self.assertEquals('me', player.name)


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(1, [Player(), Player()])
        self.game.is_the_end = lambda: False

    @raises(ValueError)
    def test_one_game_must_not_have_players_with_the_same_name(self):
        Game(1, [Player(name='x'), Player(name='x')])

    def test_summary(self):
        report = self.game.summary()
        self.assertEquals(True, 'winners' in list(report.keys()))
        self.assertEquals(True, 'losers' in list(report.keys()))
        self.assertEquals(True, 'error' in list(report.keys()))
        self.assertEquals(False, report['draw'])
        self.assertEquals(False, report['no_contest'])
        self.assertEquals([], report['error_responsibles'])
        self.assertEquals(None, report['error'])
        self.assertEquals(None, report['error_message'])

    def test_error_must_set_reason_and_responsible(self):
        p = Player()
        try:
            self.game.set_runtime_error(p, 'some error', Exception('some error'))
        except AlgorithmError:
            pass
        self.assertEquals('some error', self.game.error_message)
        self.assertEquals([str(p)], self.game.error_responsibles)

    def test_random_is_reproducible(self):
        game1 = Game(1, [])
        game2 = Game(1, [])
        self.assertEquals(game1.random.randint(1, 100), game2.random.randint(1, 100))
        self.assertEquals(game1.random.randint(1, 100), game2.random.randint(1, 100))

    def test_gat_error_generate_a_no_contest(self):
        class BuggedGame(Game):
            def play(self):
                raise Exception('ops')
        self.game = BuggedGame(1, [Player(), Player()])
        self.game.start()
        report = self.game.summary()
        self.assertEquals(True, report['no_contest'])


class TurnBasedGameTests(unittest.TestCase):
    def setUp(self):
        self.p1 = Player(name='p1')
        self.p2 = Player(name='p2')
        self.game = TurnBasedGame(1, [self.p1, self.p2])
        self.game.is_the_end = lambda: True

    def test_each_player_play_at_a_time_in_cycles(self):
        p1 = self.game.players[0]
        p2 = self.game.players[1]
        self.assertEquals(p1, self.game.next_player())
        self.game.player_in_turn = p1
        self.assertEquals(p2, self.game.next_player())
        self.game.player_in_turn = p2
        self.assertEquals(p1, self.game.next_player())

    def test_must_start_new_cycle_if_all_players_has_played(self):
        p1 = self.game.players[0]
        p2 = self.game.players[1]
        self.game.player_in_turn = None
        self.assertEquals(True, self.game.must_start_new_cycle())
        self.game.player_in_turn = p1
        self.assertEquals(False, self.game.must_start_new_cycle())
        self.game.player_in_turn = p2
        self.assertEquals(True, self.game.must_start_new_cycle())

    def test_player_strategy_may_raise_exceptions(self):
        class BuggedPlayer(Player):
            def play(self, context, **kwargs):
                raise Exception('ops')
        self.p2 = BuggedPlayer('bugged')
        self.game = TurnBasedGame(1, [self.p1, self.p2])
        self.game.is_the_end = lambda: False
        result = self.game.start()
        self.assertEquals('ops', result['error_message'])
        self.assertEquals([str(self.p2)], result['error_responsibles'])
        self.assertEquals(str(self.p1), result['winners'][0])
        self.assertEquals(str(self.p2), result['losers'][0])


class GameCompositeTests(unittest.TestCase):
    def setUp(self):
        self.game = GameComposite(1, [Player(), Player()])
        self.game.is_the_end = lambda: True

    def test_new_round(self):
        newround = self.game.new_round()
        self.assertEquals(True, isinstance(newround, self.game.Round))
        # self.assertEquals(1, len(self.game.games))

    def test_propagate_seed_to_rounds_and_it_is_reproducible(self):
        game2 = GameComposite(self.game.seed, [Player(), Player()])
        self.assertEquals(self.game.new_round().seed, game2.new_round().seed)
        self.assertEquals(self.game.new_round().seed, game2.new_round().seed)

    def test_propagate_players_to_rounds(self):
        newround = self.game.new_round()
        self.assertEquals(self.game.players, newround.players)

    def test_propagate_custom_attrs_to_rounds(self):
        self.game = GameComposite(1, [Player(), Player()], x=2)
        newround = self.game.new_round()
        self.assertEquals(2, newround.kwargs['x'])
