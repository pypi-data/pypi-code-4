from my_math import *
from my_strings import *
#import my_strings
from miedema import get_energy
from cif_to_poscar import *

def assign_type(string):
    res = string
    try:
        res = float(string)
    except ValueError:
        pass
    try:
        res = int(string)
    except ValueError:
        pass
    if string.lower() == 'true':
        res = True
    elif string.lower() == 'false':
        res = False
    elif string.lower() == 'none':
        res = None
    return res

def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)
