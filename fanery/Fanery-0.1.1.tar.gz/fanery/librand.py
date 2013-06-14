from random import randint, randrange, sample, shuffle, choice
from random import getrandbits as randbits
from random import uniform, random
from os import urandom as randbytes
from uuid import uuid4 as randuuid

def randpasswd(size = 12):
    if not (isinstance(size, (int, long)) and size > 0):
        raise ValueError('size must be positive number')
    from string import printable
    chars = list(set(printable.strip()))
    shuffle(chars)
    return ''.join(sample(chars, size))

def randfloat(*args):
    return uniform(*args) if args else random()

def randnum(*args, **argd):
    exp = argd.get('exp', 300)
    sign = choice([1, -1])
    try:
        return sign * pow(randfloat(*args), randint(-exp,exp))
    except OverflowError:
        return randnum(*args, **argd)
