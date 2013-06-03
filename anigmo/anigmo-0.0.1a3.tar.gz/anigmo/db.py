# -*- coding: utf-8 -*-
"""
anigma.db - methods and classes used for precomputed ply- databases
"""

import json
import zlib

from .util import chunks, EMPTY, get_enemy, MAX
from clint.textui import progress


class Database(object):
    def __init__(self, filename):
        self.filename = filename
        self.data = {}

    def convert(self):
        f = open(self.filename, "r")
        raw_content = [line.strip() for line in f]
        f.close()
        for line in progress.bar(raw_content):
            #print line
            values = line.split(',')
            result = values[42]
            del values[42]
            new_values = []
            for i in values:
                if i == 'o':
                    new_values.append("O")
                elif i == 'x':
                    new_values.append("X")
                else:
                    new_values.append("-")
            board = list(chunks(new_values, 6))
            key = repr(board)
            #print key
            if result == 'win':
                self.data[key] = 'X'
            elif result == 'loss':
                self.data[key] = 'O'
            else:
                self.data[key] = '-'
            #if board[3].count('-') == 0 and board[3][0] == 'X' and board[3][1] == 'X' and \
            #        board[0][0] == 'O' and board[2][0] == 'O':
            #    import pprint
            #    pprint.pprint(board)
        with open("connect4.json", "w") as nf:
            nf.write(zlib.compress(json.dumps(self.data)))

    def convertBit(self):
        f = open(self.filename, "r")
        raw_content = [line.strip() for line in f]
        f.close()
        for line in progress.bar(raw_content):
            #print line
            values = line.split(',')
            result = values[42]
            del values[42]
            board = list(chunks(values, 6))
            xBoard = 1 << 1
            oBoard = 1 << 1
            for i in xrange(7 - 1, -1, -1):
                for k in xrange(6 - 1, -1, -1):
                    if board[i][k] == 'x':
                        xBoard |= 1
                    elif board[i][k] == 'o':
                        oBoard |= 1
                    xBoard = xBoard << 1
                    oBoard = oBoard << 1
                xBoard = xBoard << 1
                oBoard = oBoard << 1
            xBoard = xBoard >> 2
            oBoard = oBoard >> 2
            xBoard = xBoard & 140737488355327
            oBoard = oBoard & 140737488355327
            key = hash(str(oBoard) + 'x' + str(xBoard))
            #print key
            if result == 'win':
                self.data[key] = 'X'
            elif result == 'loss':
                self.data[key] = 'O'
            else:
                self.data[key] = '-'
        with open("connect4bit.json", "w") as nf:
            nf.write(zlib.compress(json.dumps(self.data)))

    def convertBit2(self):
        f = open(self.filename, "r")
        raw_content = [line.strip() for line in f]
        f.close()
        for line in progress.bar(raw_content):
            #print line
            values = list(line)
            result = values[42]
            board = list(chunks(values[:42], 6))
            #print board
            xBoard = 1 << 1
            oBoard = 1 << 1
            for i in xrange(7 - 1, -1, -1):
                for k in xrange(6 - 1, -1, -1):
                    if board[i][k] == 'x':
                        xBoard |= 1
                    elif board[i][k] == 'o':
                        oBoard |= 1
                    xBoard = xBoard << 1
                    oBoard = oBoard << 1
                xBoard = xBoard << 1
                oBoard = oBoard << 1
            xBoard = xBoard >> 2
            oBoard = oBoard >> 2
            xBoard = xBoard & 140737488355327
            oBoard = oBoard & 140737488355327
            key = hash(str(oBoard) + 'x' + str(xBoard))
            #print key
            if result == '+':
                self.data[key] = 'X'
            elif result == '-':
                self.data[key] = 'O'
            else:
                self.data[key] = '-'
        with open("connect4bit.json", "w") as nf:
            nf.write(zlib.compress(json.dumps(self.data)))

    def focusDB(self, orig, new):
        pass

    def load(self):
        f = open(self.filename, "r")
        self.data = json.loads(zlib.decompress(f.read()))
        #print self.data
        print "Loaded opening book: %s with %d positions" % (self.filename, len(self.data))


# Essentially based on positions

class PlyDatabase(Database):
    def __init__(self, filename, depth):
        self.plyDepth = depth
        super(PlyDatabase, self).__init__(filename)

    def simplePositionSearch(self, node, player):
        self.originalPlayer = player
        return self.run(node, get_enemy(player), node.currentDepth())

    def run(self, node, player, depth, alpha=-MAX, beta=MAX):
        #print depth
        if depth == self.plyDepth:
            for i in node.fliphash():
                hsh = unicode(i)
                try:
                    if self.data[hsh] == self.originalPlayer:
                        return -MAX
                    elif self.data[hsh] == get_enemy(self.originalPlayer):
                        return MAX
                    else:
                        return 0
                except KeyError:
                    pass
                    #node.show()
            if node.winner() == self.originalPlayer:
                return MAX
            elif node.winner() == get_enemy(self.originalPlayer):
                return -MAX
            heuValue = node.heuristic(self.originalPlayer)
            if player == self.originalPlayer:
                return heuValue
            else:
                return -heuValue
        enemy = get_enemy(player)
        for move in node.available_moves(player):
            node.make_move(move, player)
            val = self.run(node, enemy, depth + 1, alpha, beta)
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
