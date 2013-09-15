import random
from string import ascii_letters
from ..arbitrary import Arbitrary, MappedArbitrary
from .utils import roundrobin, filter_possible, unique


__all__ = ['const', 'elements', 'oneof', 'bool_', 'char', 'letter']


class elements(Arbitrary):
    """ Choice from a list of constant values. """

    @Arbitrary.args_for_sample('a', 'b', 'c', 'd')
    def __init__(self, *el_list):
        self.el_list = el_list

    def could_generate(self, x):
        return x in self.el_list

    def next_random(self):
        return random.choice(self.el_list)

    def gen_serial(self, amount):
        return self.el_list

    def shrink(self, x):
        for el in self.el_list:
            if el == x:
                break
            yield el


class bool_(elements):
    """ Any :mod:`bool` value (``False`` or ``True``). """

    def __init__(self):
        super(type(self), self).__init__(False, True)


class const(elements):
    """ Any constant value. """

    def __init__(self, value=None):
        elements.__init__(self, value)


class char(elements):
    """ Any single character (:mod:`string` of length one). """

    def __init__(self, chars=list(map(chr, range(0, 255)))):
        elements.__init__(self, *chars)

    @unique
    @filter_possible
    def shrink(self, x):
        yield 'a'
        yield 'z'
        yield 'A'
        yield 'Z'
        yield '0'
        yield '9'
        yield ' '
        yield self.chars[0]
        yield self.chars[-1]
        yield chr(0)
        yield chr(255)


class letter(char):
    """ Lower and upper latin letters. """

    def __init__(self):
        char.__init__(self, ascii_letters)


class oneof(Arbitrary):
    """ Choice (possible weighed) from a list of Arbitraries. """

    @Arbitrary.args_for_sample(const('a'), const('b'), const('c'))
    def __init__(self, *arbitraries):
        self.arbitraries = [arb if isinstance(arb, tuple) else (arb, 1)
                            for arb in arbitraries]

    def could_generate(self, x):
        return any(arb.could_generate(x) for arb, _ in self.arbitraries)

    def next_random(self):
        arb = random.choice_weighted(self.arbitraries)
        return arb.next_random()

    def gen_serial(self, amount):
        inner_series = [arb.gen_serial(amount) for arb, _ in self.arbitraries]
        return roundrobin(inner_series)

    def shrink(self, x):
        return []
