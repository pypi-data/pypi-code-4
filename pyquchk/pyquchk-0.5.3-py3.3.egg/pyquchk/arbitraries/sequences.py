from collections import namedtuple
from itertools import islice
from .arbitrary import Arbitrary, MappedArbitrary, FilteredArbitrary, \
    get_arbitrary, with_samples, add_spec_processor
from .utils import filter_possible, unique, product
from .numbers import int_
from .primitives import char, letter

__all__ = ['tuple_', 'namedtuple_', 'dict_fixkeys',
           'list_', 'list_ordered', 'list_unique',
           'set_', 'dict_',
           'bytearray_', 'bytes_',
           'str_', 'str_letters']


@Arbitrary.set_for(tuple)
@with_samples
class tuple_(Arbitrary):
    """ Tuple with specified elements. """

    @Arbitrary.args_for_sample((int_, letter))
    def __init__(self, arbitraries):
        self.arbitraries = list(map(get_arbitrary, arbitraries))

    def could_generate(self, x):
        return all(arb.could_generate(y)
                   for arb, y in zip(self.arbitraries, x))

    def next_random(self):
        return tuple(arb.next_random() for arb in self.arbitraries)

    def gen_serial(self):
        return product(*[arb.gen_serial()
                         for arb in self.arbitraries])

    def shrink(self, x):
        for i, (arb, y) in enumerate(zip(self.arbitraries, x)):
            for shr_y in arb.shrink(y):
                yield x[:i] + (shr_y,) + x[i + 1:]


@add_spec_processor
def tuple_proc(spec):
    if isinstance(spec, tuple):
        return tuple_(map(get_arbitrary, spec))


@Arbitrary.set_for(namedtuple)
class namedtuple_(MappedArbitrary):
    def __init__(self, typename, fields):
        self.tupletype = namedtuple(typename, [name for name, _ in fields])
        self.inner_arb = tuple_([value for _, value in fields])

    def pack(self, tup):
        return self.tupletype._make(tup)

    def unpack(self, ntup):
        return tuple(ntup)


class dict_fixkeys(MappedArbitrary):
    def __init__(self, items_lst=None, **items_dct):
        self.inner_arb = namedtuple_('DictItems',
                                     items_lst or items_dct.items())

    def pack(self, ntup):
        return dict(ntup._asdict())

    def unpack(self, dct):
        ttype = self.inner_arb.tupletype
        return ttype._make([dct[name] for name in ttype._fields])


@Arbitrary.set_for(list)
@with_samples
class list_(Arbitrary):
    """ List with configurable length and elements. """

    @Arbitrary.args_for_sample(length=int_(0, 10), elements=int_(-100, 100))
    def __init__(self, length=int_(0, 20), elements=int_):
        self.length = get_arbitrary(length)
        self.elements = get_arbitrary(elements)

    def could_generate(self, x):
        return self.length.could_generate(len(x)) and \
               all(self.elements.could_generate(el) for el in x)

    def next_random(self):
        return [self.elements.next_random()
                for _ in range(self.length.next_random())]

    @unique
    @filter_possible
    def gen_serial(self):
        def gen_for_depth(depth):
            for l in self.length.gen_serial():
                if l > depth:
                    continue

                if l == 0:
                    yield []
                else:
                    el_amount = depth + 1
                    elems = list(islice(self.elements.gen_serial(), el_amount))
                    for res in product(elems, repeat=l):
                        yield list(res)

        for depth in range(50):
            for item in gen_for_depth(depth):
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

            for i, y in enumerate(x):
                for shr_y in self.elements.shrink(y):
                    yield x[:i] + [shr_y] + x[i + 1:]
        elif l == 1:
            for el in self.elements.shrink(x[0]):
                yield [el]


@add_spec_processor
def list_proc(spec):
    if isinstance(spec, list) and len(spec) == 1:
        return list_(elements=get_arbitrary(spec[0]))


@with_samples
class list_ordered(MappedArbitrary):
    """ List where elements are in order.

    .. note::

        Non-unique serially-generated values and shrink results are possible.
    """

    @Arbitrary.args_for_sample(length=int_(0, 10), elements=int_(-100, 100))
    def __init__(self, length=int_(0, 20), elements=int_,
                 key=lambda x: x, reverse=False):
        self.inner_arb = list_(length=length, elements=elements)
        self.key = key
        self.reverse = reverse

    def pack(self, lst):
        return list(sorted(lst, key=self.key, reverse=self.reverse))

    def unpack(self, lst):
        return lst


@with_samples
class list_unique(FilteredArbitrary):
    """ List with unique elements.

    .. warning::

        Implementation just keeps generating random lists until one with
        unique elements is found, so for some parameters it can be very slow.
        Also, upper length bound is never reached in some cases.
    """

    @Arbitrary.args_for_sample(length=int_(0, 10), elements=int_(-100, 100))
    def __init__(self, length=int_(0, 20), elements=int_):
        self.inner_arb = list_(length=length, elements=elements)

    def predicate(self, lst):
        return len(set(lst)) == len(lst)


@Arbitrary.set_for(set)
@with_samples
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
@with_samples
class dict_(MappedArbitrary):
    """ Dictionary with specified items (key-value pairs) arbitrary.

    .. note::

        Non-unique serially-generated values and shrink results are possible.
    """

    def __init__(self,
                 length=int_(0, 20),
                 keys=int_, values=int_):
        self.inner_arb = tuple_((list_unique(length=length, elements=keys),
                                 list_(length=length, elements=values)))

    def pack(self, tup):
        keys, values = tup
        return dict(zip(keys, values))

    def unpack(self, dct):
        items = list(dct.items())
        keys, values = zip(*items)
        return (list(keys), list(values))

    @unique
    def gen_serial(self):
        return super(dict_, self).gen_serial()


@Arbitrary.set_for(bytearray)
@with_samples
class bytearray_(MappedArbitrary):
    """ Mutable bytearray with configurable length and elements. """

    def __init__(self, length=int_(0, 20), elements=int_(0, 255)):
        self.inner_arb = list_(length=length, elements=elements)

    def pack(self, lst):
        return bytearray(lst)

    def unpack(self, barr):
        return list(barr)


@with_samples
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
@with_samples
class str_(MappedArbitrary):
    """ String with configurable length and characters. """

    def __init__(self, length=int_(0, 20), chars=char):
        self.inner_arb = list_(length=length, elements=chars)

    def pack(self, lst):
        return ''.join(lst)

    def unpack(self, s):
        return list(s)


@with_samples
class str_letters(str_):
    """ String consisting of letters only. """

    def __init__(self, length=int_(0, 20)):
        str_.__init__(self, length=length, chars=letter)
