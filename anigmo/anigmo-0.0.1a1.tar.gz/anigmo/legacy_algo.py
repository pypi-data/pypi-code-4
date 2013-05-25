class Minimax(AbstractAlgorithm):
    def run(self, node, player):
        self.originalPlayer = player
        return self.wrap(node, get_enemy(player))

    def check(self, node, player):
        return self.check_base(node, self.originalPlayer)

    def wrap(self, node, player):
        check = self.check(node, player)
        if check is not None:
            return check
        return self.iterate(node, player)

    def iterate(self, node, player):
        best = None
        for move in node.available_moves():
            node.make_move(move, player)
            val = self.wrap(node, get_enemy(player))
            node.remove_move(move, player)
            if player == self.originalPlayer:
                if best is None or val > best:
                    best = val
            else:
                if best is None or val < best:
                    best = val
        return best

class Negamax(Minimax):
    def run(self, node, player):
        self.originalPlayer = player
        return -self.wrap(node, get_enemy(player))

    def check(self, node, player):
        return self.check_base(node, player)

    def iterate(self, node, player):
        best = -MAX
        for move in node.available_moves():
            node.make_move(move, player)
            best = max(best, -self.wrap(node, get_enemy(player)))
            node.remove_move(move, player)
        return best

class AlphaBeta(Minimax):
    def wrap(self, node, player, alpha=-MAX, beta=MAX):
        check = self.check(node, player)
        if check is not None:
            return check
        return self.iterate(node, player, alpha, beta)

    def iterate(self, node, player, alpha, beta):
        for move in node.moveOrdering(node.available_moves()):
            node.make_move(move, player)
            val = self.wrap(node, get_enemy(player), alpha, beta)
            node.remove_move(move, player)
            if player == self.originalPlayer:
                if val > alpha:
                    alpha = val
                if alpha >= beta:
                    return beta
            else:
                if val < beta:
                    beta = val
                if beta <= alpha:
                    return alpha
        if player == self.originalPlayer:
            return alpha
        else:
            return beta


class NegaAlphaBeta(AlphaBeta, Negamax):
    def iterate(self, node, player, alpha, beta):
        for move in node.moveOrdering(node.available_moves()):
            node.make_move(move, player)
            val = -self.wrap(node, get_enemy(player), -beta, -alpha)
            node.remove_move(move, player)
            if val >= beta:
                return val
            if val >= alpha:
                alpha = val
        return alpha
