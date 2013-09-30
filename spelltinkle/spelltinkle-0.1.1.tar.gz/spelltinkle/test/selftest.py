import os
import pstats
import shutil
import cProfile

from ..keys import keynames
from ..run import run
from .tests import all_tests
import spelltinkle.test.tests as tests

from logging import debug


class Input:
    session = None

    def __init__(self, test):
        self.stream = self.characters(test)

    def __call__(self):
        c = next(self.stream)
        return c
    
    def characters(self, test):
        for s in test(self.session):
            while s:
                s0 = s
                if s[:2] == '^^':
                    yield '^'
                    s = s[2:]
                if s[0] == '^':
                    yield s[:2]
                    s = s[2:]
                elif s[:2] == '<<':
                    yield '<'
                    s = s[2:]
                elif s[0] == '<':
                    key, s = s[1:].split('>', 1)
                    yield key.replace('-','_')
                elif s[0] == '\n':
                    s = s[1:]
                else:
                    yield s[0]
                    s = s[1:]
                debug(s0[:len(s0) - len(s)])
                

def test(names):
    if os.path.isdir('ecat-self-test'):
        shutil.rmtree('ecat-self-test')
    os.mkdir('ecat-self-test')
    os.chdir('ecat-self-test')
    prof = cProfile.Profile()
    prof.enable()
    if not names:
        names = all_tests
    for name in names:
        debug(name)
        t = getattr(tests, name)
        input = Input(t)
        run(getattr(t, 'args', []), input)
    prof.disable()
    prof.dump_stats('test.profile')
    #stats = pstats.Stats('test.profile')
    #stats.sort_stats('time').print_stats(20)
