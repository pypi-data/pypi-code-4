from math import ceil, sqrt
from itertools import product, islice, count
from .arbitrary import Arbitrary, MappedArbitrary, FilteredArbitrary
from .utils import filter_possible, unique
from .numbers import int_
from .primitives import char, letter

__all__ = ['tuple_',
           'list_', 'list_ordered', 'list_unique',
           'set_', 'dict_',
           'bytearray_', 'bytes_',
           'str_', 'str_letters']


class tuple_(Arbitrary):
    """ Tuple with specified elements. """

    @Arbitrary.args_for_sample(int_, letter)
    def __init__(self, *arbitraries):
        self.arbitraries = arbitraries

    def could_generate(self, x):
        return all(arb.could_generate(y)
                   for arb, y in zip(self.arbitraries, x))

    def next_random(self):
        return tuple(arb.next_random() for arb in self.arbitraries)

    def gen_serial(self, amount):
        inner_amount = int(ceil(sqrt(amount)))
        return product(*[arb.gen_serial(inner_amount)
                         for arb in self.arbitraries])

    def shrink(self, x):
        for i, (arb, y) in enumerate(zip(self.arbitraries, x)):
            for shr_y in arb.shrink(y):
                yield x[:i] + (shr_y,) + x[i + 1:]


@Arbitrary.set_for(list)
class list_(Arbitrary):
    """ List with configurable length and elements. """

    @Arbitrary.args_for_sample(length=int_(0, 5), elements=int_(-100, 100))
    def __init__(self, length=int_(0, 20), elements=int_):
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


class list_ordered(MappedArbitrary):
    """ List where elements are in order.

    .. note::

        Non-unique serially-generated values and shrink results are possible.
    """

    def __init__(self, length=int_(0, 20), elements=int_,
                 key=lambda x: x, reverse=False):
        self.inner_arb = list_(length=length, elements=elements)
        self.key = key
        self.reverse = reverse

    def pack(self, lst):
        return list(sorted(lst, key=self.key, reverse=self.reverse))

    def unpack(self, lst):
        return lst


class list_unique(FilteredArbitrary):
    """ List with unique elements.

    .. warning::

        Implementation just keeps generating random lists until one with
        unique elements is found, so for some parameters it can be very slow.
        Also, upper length bound is never reached in some cases.
    """

    def __init__(self, length=int_(0, 20), elements=int_):
        self.inner_arb = list_(length=length, elements=elements)

    def predicate(self, lst):
        return len(set(lst)) == len(lst)


@Arbitrary.set_for(set)
class set_(MappedArbitrary):
    """ Set of unique elements.

    .. warning::

        Implementation just keeps generating random lists until one with
        unique elements is found, so for some parameters it can be very slow.
        Also, upper length bound is never reached in some cases.

    .. note::

        Non-unique serially-generated values and shrink results are possible.
    """

    def __init__(self, length=int_(0, 20), elements=int_):
        self.inner_arb = list_unique(length=length, elements=elements)

    def pack(self, lst):
        return set(lst)

    def unpack(self, set_val):
        return list(set_val)


@Arbitrary.set_for(dict)
class dict_(MappedArbitrary):
    """ Dictionary with specified items (key-value pairs) arbitrary.

    .. note::

        Non-unique serially-generated values and shrink results are possible.
    """

    def __init__(self,
                 length=int_(0, 20),
                 items=None,
                 keys=int_, values=int_):
        if items is None:
            items = tuple_(keys, values)
        self.inner_arb = list_(length=length, elements=items)

    def pack(self, lst):
        return dict(lst)

    def unpack(self, dct):
        return list(dct.items())


@Arbitrary.set_for(bytearray)
class bytearray_(MappedArbitrary):
    """ Mutable bytearray with configurable length and elements. """

    def __init__(self, length=int_(0, 20), elements=int_(0, 255)):
        self.inner_arb = list_(length=length, elements=elements)

    def pack(self, lst):
        return bytearray(lst)

    def unpack(self, barr):
        return list(barr)


class bytes_(MappedArbitrary):
    """ Immutable bytearray with configurable length and elements.

    .. note::

        In Python 2 it's the same as :class:`str_`.
    """

    def __init__(self, length=int_(0, 20), elements=int_(0, 255)):
        self.inner_arb = bytearray_(length=length, elements=elements)

    def pack(self, barr):
        return bytes(barr)

    def unpack(self, bs):
        return bytearray(bs)


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
