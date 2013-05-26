#!/usr/bin/env python

NORTH = 1
EAST = 2
SOUTH = -1
WEST = -2
UNDEFINED = 0

database = []

import pdb, sys

from copy import copy
import time


class GridGame(object):
    """
    0 1 2 .
    1
    2
    .
    """
    def __init__(self):
        self.width = 8
        self.height = 6
        self.pos = [0, 0]  # x, y
        self.numTurns = 0  # first move is always a turn
        self.numMoves = 0
        self.currentDirection = UNDEFINED
        self.history = [([0, 0], UNDEFINED, 0)]

    def available_moves(self):
        moves = []
        if self.pos[0] + 1 < self.width:
            moves.append(EAST)
        if self.pos[1] + 1 < self.height:
            moves.append(SOUTH)
        if self.pos[0] > 0:
            moves.append(WEST)
        if self.pos[1] > 0:
            moves.append(NORTH)
        return moves

    def make_move(self, move):
        if move != self.currentDirection:
            if self.currentDirection != UNDEFINED:
                self.numTurns += 1
            self.currentDirection = move
        self.history.append((copy(self.pos), move, self.numTurns))
        if move == WEST:
            self.pos[0] -= 1
        elif move == EAST:
            self.pos[0] += 1
        elif move == SOUTH:
            self.pos[1] += 1
        elif move == NORTH:
            self.pos[1] -= 1
        self.numMoves += 1

    def remove_move(self, move):
        #if self.currentDirection != self.history[-2][1]:
        #   self.numTurns -= 1
        self.numTurns = self.history[-2][2]
        self.currentDirection = self.history[-2][1]
        self.pos = self.history[-1][0]
        self.history.pop(-1)
        self.numMoves -= 1


G = GridGame()


def printHistory(history):
    for item in history:
        if item[1] == WEST:
            sys.stdout.write("W")
        elif item[1] == EAST:
            sys.stdout.write("E")
        elif item[1] == SOUTH:
            sys.stdout.write("S")
        elif item[1] == NORTH:
            sys.stdout.write("N")
        else:
            sys.stdout.write("-")
    sys.stdout.write("\n")


def iterate_paths_length(len):
    #print G.numMoves
    if G.numMoves == len and G.pos == [7, 5]:
            printHistory(G.history)
            return 1
            #print numberTotalPathLength
    elif (len - G.numMoves) < ((7 - G.pos[0]) + (5 - G.pos[1])):
        return 0  # is it still possible to reach it?
    else:
        total = 0
        for move in G.available_moves():
            G.make_move(move)
            total += iterate_paths_length(len)
            G.remove_move(move)
        return total
    return 0


def iterate_paths_turns(turn):
    #print G.numMoves
    if G.numTurns == turn and G.pos == [7, 5]:
            printHistory(G.history)
            return 1
            #print numberTotalPathLength
    elif G.numTurns > turn:
        return 0  # is it still possible to reach it?
    else:
        total = 0
        for move in G.available_moves():
            #print G.history, G.numTurns
            #pdb.set_trace()
            G.make_move(move)
            total += iterate_paths_turns(turn)
            G.remove_move(move)
        return total
    return 0


def iterate_paths_combo(len, turn):
    #print G.numMoves
    if G.numTurns == turn and G.numMoves == len and G.pos == [7, 5]:
            printHistory(G.history)
            return 1
            #print numberTotalPathLength
    elif (G.numTurns > turn) or (len - G.numMoves) < ((7 - G.pos[0]) + (5 - G.pos[1])):
        return 0  # is it still possible to reach it?
    else:
        total = 0
        for move in G.available_moves():
            #print G.history, G.numTurns
            #pdb.set_trace()
            G.make_move(move)
            total += iterate_paths_combo(len, turn)
            G.remove_move(move)
        return total
    return 0

if sys.argv[1] == "len":
    print iterate_paths_length(int(sys.argv[2]))
elif sys.argv[1] == "turn":
    print iterate_paths_turns(int(sys.argv[2]))
else:
    print iterate_paths_combo(int(sys.argv[2]), int(sys.argv[3]))

