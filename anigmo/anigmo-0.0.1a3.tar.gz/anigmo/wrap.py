# -*- coding: utf-8 -*-
"""
anigma.core - the brain
"""


class AbstractWrapper(object):
    def __init__(self):
        pass

    def run(self):
        self.setUp()
        self.determine()
        self.finish()

    def setUp(self):
        if self.algo.values:
            game.values = self.algo.values
        game.init()
        self.values = {}

    def finish(self):
        choices = []
        for move, val in values.iteritems():
            if val > a:
                a = val
                choices = [move]
            elif val == a:
                choices.append(move)
        return random.choice(choices)


class SimpleWrapper(AbstractWrapper):
    pass


class MultiProcessWrapper(AbstractWrapper):
    pass
