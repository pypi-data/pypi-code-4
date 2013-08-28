# coding: utf-8
import random

from gat_games.game_engine.engine import *

# http://en.wikipedia.org/wiki/Chess


class ChessNativePlayer(Player):
    def play(self, context, **kwargs):
        pass


class RandomChessPlayer(ChessNativePlayer):
    def play(self, context, **kwargs):
        option = random.randint(0, 10)


class Move(GameCommand):
    def validate(self, game, context):
        origin = self.kwargs.get('origin')
        target = self.kwargs.get('target')
        if game.player_in_turn != self.player:
            raise InvalidCommandError('It is not your turn')
        raise InvalidCommandError('Invalid piece movement: %s-%s' % (origin, target))
        raise InvalidCommandError('Invalid movement because checkmate threat: %s-%s' % (origin, target))

    def execute(self, game):
        pass


class ChessPiece(object):
    '''
    Conventions: White starts in the bottom and Black in the top.
    '''
    WHITE = 'W'
    BLACK = 'B'

    def __init__(self, color):
        self.color = color

    def name(self):
        return '%s-%s' % (self.color, self.__class__.__name__.lower())

    def is_diagonal_movement(self, x, y, fx, fy):
        return abs(fy - y) == abs(fx - x)

    def is_horizontal_movement(self, x, y, fx, fy):
        return y == fy and x != fx

    def is_vertical_movement(self, x, y, fx, fy):
        return x == fx and y != fy

    def is_forward_movement(self, x, y, fx, fy):
        if self.color == ChessPiece.WHITE:
            return fy > y
        else:
            return fy < y

    def is_backward_movement(self, x, y, fx, fy):
        return not self.is_forward_movement(x, y, fx, fy)

    def is_valid_movement(self, x, y, fx, fy): # x => column, y => line
        pass


class Pawn(ChessPiece):
    def is_valid_position(self, x, y, fx, fy):
        if self.color == ChessPiece.WHITE:
            if y == 0 or fy == 0:
                return False
        else:
            if y == 7 or fy == 7:
                return False
        return True

    def is_first_movement(self, x, y, fx, fy):
        if self.color == ChessPiece.WHITE and y == 1:
            return True
        if self.color == ChessPiece.BLACK and y == 6:
            return True
        return False

    def is_capturing_another_piece(self, x, y, fx, fy):
        return False # FIXME self.board[fx][fy] != None

    def is_valid_movement(self, x, y, fx, fy):
        if not self.is_valid_position(x, y, fx, fy):
            return False
        if self.is_horizontal_movement() or self.is_backward_movement():
            return False
        if self.is_first_movement(x, y, fx, fy):
            if self.is_vertical_movement(x, y, fx, fy):
                if self.color == ChessPiece.WHITE:
                    if fy == 2 or fy == 3:
                        return True # FIXME squares tem que estarem vazios
                else:
                    if fy == 5 or fy == 4:
                        return True # FIXME squares tem que estarem vazios
            # if self.is_capturing_another_piece(x, y, fx, fy):
            #     pass
        # if self.is_capturing_another_piece(x, y, fx, fy):
        #     pass
        return True


class ChessBoard(object):
    def __init__(self, current_color=ChessPiece.WHITE, board={}):
        self.current_color = current_color
        self.board = board

    def create_initial_board(self):
        self.board = [  # a b c d e f g h
                        [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK], # 8
                        [PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN], # 7
                        [None]*8, # 6
                        [None]*8, # 5
                        [None]*8, # 4
                        [None]*8, # 3
                        [PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN], # 2
                        [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK], # 1
                    ]

    def valid_movements(self):
        movements = []
        for i in list(range(0, 8)):
            for j in list(range(0, 8)):
                unit = self.board[i][j]
                movements.extend([])
        return movements

    def is_check(self):
        pass

    def is_checkmate(self):
        return self.is_check() and not bool(self.valid_movements())

    def is_valid_movement(self, origin, target):
        return '' in self.valid_movements()

    def change_player(self):
        if self.current_color == ChessPiece.WHITE:
            self.current_color = ChessPiece.BLACK
        else:
            self.current_color = ChessPiece.WHITE

    def move(self, origin, target):
        self.board[target[0]][target[1]] = self.board[origin[0]][origin[1]]
        self.board[origin[0]][origin[1]] = None
        self.change_player()
        return ChessBoard(current_color=self.current_color, board=self.board)


# Chess => board => valid movements
# ChessGame
#  - board
#  - current color turn (associar jogador a branco ou preto)
#  - valid movements:
#       current color:
#         pega todas as peças
#   is check?
#   is checkmate?
# possible moviments


# En passant: peao
    # test king+tower: Castling
# Promotion: pawn vira qq coisa
# The king moves one square in any direction. The king has also a special move which is called castling and involves also moving a rook.
# The rook can move any number of squares along any rank or file, but may not leap over other pieces. Along with the king, the rook is involved during the king's castling move.
# The bishop can move any number of squares diagonally, but may not leap over other pieces.
# The queen combines the power of the rook and bishop and can move any number of squares along rank, file, or diagonal, but it may not leap over other pieces.
# The knight moves to any of the closest squares that are not on the same rank, file, or diagonal, thus the move forms an "L"-shape: two squares vertically and one square horizontally, or two squares horizontally and one square vertically. The knight is the only piece that can leap over other pieces.
# The pawn may move forward to the unoccupied square immediately in front of it on the same file; or on its first move it may advance two squares along the same file provided both squares are unoccupied; or it may move to a square occupied by an opponent's piece which is diagonally in front of it on an adjacent file, capturing that piece. The pawn has two special moves: the en passant capture and pawn promotion.
    def move(self, current_cell, final_cell):
        unit = self.board.get(current_cell, None)
        if not unit or not self.is_valid_movement(current_cell, final_cell):
            raise AlgorithmError('Invalid movement')
        else:
            self.board[final_cell] = self.board[current_cell]
            del self.board[current_cell]

    def to_dict(self):
        pass


class Chess(TurnBasedGame):
    RandomStrategy = RandomChessPlayer
    Player = ChessPlayer

    PAWN = 'pawn'
    KNIGHT = 'knight'
    BISHOP = 'bishop'
    ROOK = 'rook'
    QUEEN = 'queen'
    KING = 'king'
    pieces = [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]

    def prepare(self): pass
    def get_context(self, player): return super(Game, self).get_context(player)
    def before_play(self): pass
    def play(self): pass
    def after_play(self): pass
    def is_the_end(self): return True
    def the_end(self): pass
    def summary(self): return super(Game, self).summary()

    def is_game_over(self):
        # Although the objective of the game is to checkmate the opponent, chess games do not have to end in checkmate—either player may resign which is a win for the other player. It is considered bad etiquette to continue playing when in a truly hopeless position.[3] If it is a game with time control, a player may run out of time and lose, even with a much superior position. Games also may end in a draw (tie). A draw can occur in several situations, including draw by agreement, stalemate, threefold repetition of a position, the fifty-move rule, or a draw by impossibility of checkmate (usually because of insufficient material to checkmate). As checkmate from some positions cannot be forced in fewer than 50 moves (such as in the pawnless chess endgame and two knights endgame), the fifty-move rule is not applied everywhere,[note 2] particularly in correspondence chess.
        return False

    def get_context(self, player):
        context = super(Chess, self).get_context(player)
        return context

    def summary(self):
        s = super(Chess, self).summary()
        s.update({
        })
        return s

    def the_end(self):
        self.winner = None
        self.loser = None
        self.draw = None
        return super(Chess, self).the_end()

    def player_finished_his_turn(self):
        pass
