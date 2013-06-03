# -*- coding: utf-8 -*-
"""
anigmo.util - the helpers
"""

#import showme

MAX = 2147483647  # sys.maxint - 1
EMPTY = '-'


def get_enemy(player):
    """Returns the enemy player. The player to move next.

    :param player: current player
    """
    if type(player) == int:
        return -player
    if player == 'X':
        return 'O'
    return 'X'


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


#http://graphics.stanford.edu/~seander/bithacks.html#CountBitsSetKernighan
def popcount_kernighan(v):
    c = 0
    while v:
        v &= v - 1
        c += 1
    return c

#http://graphics.stanford.edu/~seander/bithacks.html#CountBitsSetTable
POPCOUNT_TABLE16 = [0] * 2**16
for index in xrange(len(POPCOUNT_TABLE16)):
    POPCOUNT_TABLE16[index] = (index & 1) + POPCOUNT_TABLE16[index >> 1]


def popcount32_table16(v):
    return (POPCOUNT_TABLE16[v & 0xffff] +
            POPCOUNT_TABLE16[(v >> 16) & 0xffff])


POPCOUNT32_LIMIT = 2**32-1
POPCOUNT_TABLE8 = [0] * 2**8
for index in xrange(len(POPCOUNT_TABLE8)):
    POPCOUNT_TABLE8[index] = (index & 1) + POPCOUNT_TABLE8[index >> 1]


def popcount_hybrid(v):
    if v <= POPCOUNT32_LIMIT:
        return (POPCOUNT_TABLE16[v & 0xffff] +
                POPCOUNT_TABLE16[(v >> 16) & 0xffff])
    else:
        c = 0
        while v:
            v &= v - 1
            c += 1
        return c
