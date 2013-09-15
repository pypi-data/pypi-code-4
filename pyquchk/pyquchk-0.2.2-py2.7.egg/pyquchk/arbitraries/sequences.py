from math import ceil, sqrt
from itertools import product, islice, count
from ..arbitrary import Arbitrary, MappedArbitrary
from .utils import filter_possible, unique
from .numbers import int_
from .primitives import char, letter

__all__ = ['list_', 'bytearray_', 'bytes_', 'str_', 'str_letters']


@Arbitrary.set_for(list)
class list_(Arbitrary):
    """ List with configurable length and elements. """

    @Arbitrary.args_for_sample(length=int_(0, 5), elements=int_(-100, 100))
    def __init__(self, length=int_(0, 32), elements=int_):
        self.length = length
        self.elements = elements

    def could_generate(self, x):
        return self.length.could_generate(len(x)) and \
               all(self.elements.could_generate(el) for el in x)

    def next_random(self):
        return [self.elements.next_random()
                for _ in range(self.length.next_random())]

    @unique
    @filter_possible
    def gen_serial(self, amount):
        def gen_for_depth(depth, amount):
            for l in self.length.gen_serial(amount):
                if not (depth >= l or depth == 0):
                    continue

                if l == 0:
                    yield []
                else:
                    el_amount = depth + 1
                    elems = self.elements.gen_serial(el_amount)
                    for res in product(elems, repeat=l):
                        yield list(res)

        inner_amount = int(ceil(sqrt(amount)))

        for depth in count():
            for item in gen_for_depth(depth, inner_amount):
                yield item

        for l in self.length.gen_serial(amount):
            if l == 0:
                yield []
                continue

            el_amount = int(ceil(inner_amount ** (1 / l))) + 1
            elems = self.elements.gen_serial(el_amount)
            for res in islice(product(elems, repeat=l), inner_amount):
                yield list(res)

    @filter_possible
    def shrink(self, x):
        l = len(x)
        if l > 1:
            yield x[:-1]
            yield x[1:]

            yield x[:l // 3]
            yield x[l // 3:2 * l // 3]
            yield x[2 * l // 3:]

            el_gens = map(self.elements.shrink, x)
            for els in zip(*el_gens):
                yield list(els)
        elif l == 1:
            for el in self.elements.shrink(x[0]):
                yield [el]


@Arbitrary.set_for(bytearray)
class bytearray_(MappedArbitrary):
    """ Mutable bytearray with configurable length and elements. """

    def __init__(self, length=int_(0, 20), elements=int_(0, 255)):
        self.inner_arb = list_(length=length, elements=elements)

    def pack(self, lst):
        return bytearray(lst)

    def unpack(self, s):
        return list(s)


class bytes_(MappedArbitrary):
    """ Immutable bytearray with configurable length and elements.

    Same as :class:`str_` in Python 2.
    """

    def __init__(self, length=int_(0, 20), elements=int_(0, 255)):
        self.inner_arb = bytearray_(length=length, elements=elements)

    def pack(self, lst):
        return bytes(lst)

    def unpack(self, s):
        return list(s)


if bytes is not str:
    Arbitrary.set_for(bytes, bytes_)


@Arbitrary.set_for(str)
class str_(MappedArbitrary):
    """ String with configurable length and characters. """

    def __init__(self, length=int_(0, 20), chars=char):
        self.inner_arb = list_(length=length, elements=chars)

    def pack(self, lst):
        return ''.join(lst)

    def unpack(self, s):
        return list(s)


class str_letters(str_):
    """ String consisting of letters only. """

    def __init__(self, length=int_(0, 20)):
        str_.__init__(self, length=length, chars=letter)
