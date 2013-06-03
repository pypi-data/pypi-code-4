import unittest
from mock import patch

from pqhelper import easy


# silly workaround to avoid false warnings in PyCharm
patch.object = patch.object


class Test_capture_solution(unittest.TestCase):
    def test_returns_empty_sequence_if_board_not_found(self):
        with patch.object(easy._state_investigator, 'get_capture') as m_get_vs:
            m_get_vs.return_value = None
            solution = easy.capture_solution()
        # confirm empty sequence
        empty_sequence = tuple()
        self.assertSequenceEqual(solution, empty_sequence)


class Test_versus_summaries(unittest.TestCase):
    four_turn_board_string = '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             '........\n'\
                             'r.y.g.b.\n'\
                             'r.y.g.b.\n'\
                             'xrmyxgmb'

    def test_returns_empty_sequence_if_board_not_found(self):
        with patch.object(easy._state_investigator, 'get_versus') as m_get_vs:
            some_value = 1
            m_get_vs.return_value = None, some_value, some_value, 0
            summaries = easy.versus_summaries()
        # confirm empty sequence
        empty_sequence = tuple()
        self.assertSequenceEqual(summaries, empty_sequence)

    # def test_calls_advisor_reset___sims_to_average___times(self):
    #     SIMS_TO_AVERAGE = 3
    #     # get parts to be patched
    #     si = easy._state_investigator
    #     board = easy.base.Board(self.four_turn_board_string)
    #     player, opponent = si.generic_versus_actors()
    #     advisor = easy._versus_advisor
    #     advisor.reset(board, player, opponent)  # actual reset won't be called
    #     with patch.object(si, 'get_versus') as m_get_vs:
    #         m_get_vs.return_value = board, player, opponent
    #         with patch.object(advisor, 'reset') as m_reset:
    #             #todo: how to do side effect to actually reset?
    #             easy.versus_summaries(sims_to_average=SIMS_TO_AVERAGE)
    #     self.assertEqual(m_reset.call_count, SIMS_TO_AVERAGE)

    # def test_calls_advisor_simulate___sims_to_average_x_turns___times(self):
    #     SIMS_TO_AVERAGE = 3
    #     TURNS = 2
    #     si = easy._state_investigator
    #     advisor = easy._versus_advisor
    #     board = easy.base.Board(self.four_turn_board_string)
    #     player, opponent = si.generic_versus_actors()
    #     advisor.reset(board, player, opponent)  # actual reset won't be called
    #
    #     #todo: possible to just wrap real methods and get extra info about them?
    #     #todo: instead of needing to fake all the return values?
    #
    #     with patch.object(si, 'get_versus') as m_get_vs:
    #         m_get_vs.return_value = board, player, opponent
    #         with patch.object(advisor, 'simulate_next_turn') as m_sim:
    #             #todo: how to do side effect to actually reset?
    #             easy.versus_summaries(sims_to_average=SIMS_TO_AVERAGE)
    #     self.assertEqual(m_sim.call_count, SIMS_TO_AVERAGE * TURNS)


if __name__ == "__main__":
    pass