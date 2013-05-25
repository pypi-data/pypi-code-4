# -*- coding: utf-8 -*-
"""
anigma.games.abstract - An abstract Abstract game
"""


class AbstractGame(object):
    """An abstract class that is used for standardization.

    Used as the base class for all other games.

    :param board: initial custom board
    :type board: list presentation
    :var interface: Variable that defines features supported by a game class.
    """

    #: Feature defining dictionary.
    #: **normal** - ....
    #: **heuristic** - Custom Heuristic function
    #: **initial board** - Can a Game be created with a custom board.
    #: **transposition** - Are transposition tables supported.
    #: **custom board size** - Can board sizes be varied
    #: **move ordering** - Does the game implement a custom move ordering function.
    #: **enemy** - ....
    #: **opening book** - Are opening books supported.
    interface = {
        "normal": False,
        "heuristic": False,
        "transposition": False,
        "initial board": False,
        "custom board size": False,
        "move ordering": False,
        "enemy": False,
        "opennig book": False,
    }
    #interface.__doc__ = """
    def __init__(self, board=None):
        pass

    def init(self):
        pass

    def show(self):
        """Shows the current game state in the terminal"""
        pass

    def moveOrdering(self, moves):
        """Orders the moves after some game-specific importance pattern"""
        return moves

    def available_moves(self, player=None):
        """List all available moves that are left playable.

        :param player: player id, if available moves depend on player
        :rtype: list of moves
        """
        pass

    def over(self):
        """Is the game over?

        :rtype: boolean
        """
        return self.complete() or self.winner() is not None

    def complete(self):
        """Is the game complete?

        :rtype: boolean
        """
        pass

    def winner(self):
        """Is there a winner?

        :rtype: None or player
        """
        pass

    def make_move(self, position, player):
        """Make a move.

        :param position: position where to place the mark, value is game-specific
        :param player: player to make the move
        """
        pass

    def remove_move(self, position, player):
        """Remove a move.

        :param position: position where to remove the mark, value is game-specific
        :param player: player to undo the move
        """
        pass

    def reset(self):
        """Reset the board back to NULL"""
        pass

    def heuristic(self, player):
        """Returns a heuristic-value for the specified player that
        defines how good the current state is.

        :param player: player id for heuristic score
        :rtype: integer
        """
        pass

    def hash(self):
        """Uniquely hashes the current board.

        :rtype: hash()
        """
        pass
