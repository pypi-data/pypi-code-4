import random
from string import ascii_letters
from .arbitrary import Arbitrary, get_arbitrary, with_samples
from .utils import roundrobin, filter_possible, unique


__all__ = ['const', 'elements', 'oneof', 'bool_', 'char', 'letter']


@with_samples
class elements(Arbitrary):
    """ Choice from a list of constant values. """

    @Arbitrary.args_for_sample('a', 'b', 'c', 'd')
    def __init__(self, *el_list):
        self.el_list = el_list

    def could_generate(self, x):
        return x in self.el_list

    def next_random(self):
        return random.choice(self.el_list)

    def gen_serial(self):
        return self.el_list

    def shrink(self, x):
        for el in self.el_list:
            if el == x:
                break
            yield el


@Arbitrary.set_for(bool)
@with_samples
class bool_(elements):
    """ Any :mod:`bool` value (``False`` or ``True``). """

    def __init__(self):
        elements.__init__(self, False, True)


@with_samples
class const(elements):
    """ Any constant value. """

    @Arbitrary.args_for_sample(value='abc')
    def __init__(self, value=None):
        elements.__init__(self, value)


@with_samples
class char(elements):
    """ Any single character (:mod:`string` of length one). """

    def __init__(self, chars=list(map(chr, range(0, 255)))):
        elements.__init__(self, *chars)

    @unique
    @filter_possible
    def shrink(self, x):
        lst = ['a', 'z', 'A', 'Z', '0', '9', ' ',
               self.el_list[0], self.el_list[-1], chr(0), chr(255)]
        for c in lst:
            if c == x:
                break
            yield c


@with_samples
class letter(char):
    """ Lower and upper latin letters. """

    def __init__(self):
        char.__init__(self, ascii_letters)


@with_samples
class oneof(Arbitrary):
    """ Choice (possible weighed) from a list of Arbitraries. """

    @Arbitrary.args_for_sample(const('a'), const('b'), const('c'))
    def __init__(self, *arbitraries):
        arbitraries = [arb if isinstance(arb, tuple) else (arb, 1)
                       for arb in arbitraries]
        self.arbitraries = [(get_arbitrary(arb), w) for arb, w in arbitraries]

    def could_generate(self, x):
        return any(arb.could_generate(x) for arb, _ in self.arbitraries)

    def next_random(self):
        arb = random.choice_weighted(self.arbitraries)
        return arb.next_random()

    def gen_serial(self):
        inner_series = [arb.gen_serial() for arb, _ in self.arbitraries]
        return roundrobin(inner_series)

    def shrink(self, x):
        return []
