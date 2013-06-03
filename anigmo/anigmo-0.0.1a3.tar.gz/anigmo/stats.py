# -*- coding: utf-8 -*-
"""
anigmo.stats - the statistics classes
"""

import threading

from .util import get_enemy


class AbstractCounter(object):
    debug = False

    def status(self):
        self.timer = threading.Timer(10, self.status)
        if self.debug:
            print self.count
            self.timer.start()


class GameTreeCounter(AbstractCounter):
    def __init__(self):
        self.count = 0

    #@showme.cputime
    def run(self, node):
        self.status()
        self.iterate(node, 'O')
        self.timer.cancel()
        return self.count

    def iterate(self, node, player):
        if node.over():
            self.count += 1
        else:
            enemy = get_enemy(player)
            for move in node.available_moves():
                node.make_move(move, player)
                self.iterate(node, enemy)
                node.remove_move(move, player)


class StateCounter(AbstractCounter):
    def __init__(self):
        self.count = 0
        self.states = []

    #@showme.cputime
    def run(self, node):
        self.status()
        self.iterate(node, 'O')
        self.timer.cancel()
        return len(set(self.states))

    def iterate(self, node, player):
        self.states.append(str(node))
        if node.over():
            self.count += 1
        else:
            enemy = get_enemy(player)
            for move in node.available_moves():
                node.make_move(move, player)
                self.iterate(node, enemy)
                node.remove_move(move, player)


#unique keyword, set instead list

#both share code, save all states but different ones and return count in the end


class GameTreeGenerator(GameTreeCounter):
    #@showme.cputime
    def run(self, node):
        self.status()
        self.gameTree = self.iterate(node, 'O')
        self.timer.cancel()
        return self.gameTree

    def iterate(self, node, player):
        if node.over():
            self.count += 1
            return self.count
        else:
            enemy = get_enemy(player)
            level = {}
            for move in node.available_moves():
                node.make_move(move, player)
                level[str(node)] = self.iterate(node, enemy)
                node.remove_move(move, player)
            return level


class StateGenerator(StateCounter):
    def run(self, node):
        self.status()
        self.iterate(node, 'O')
        self.timer.cancel()
        return set(self.states)
