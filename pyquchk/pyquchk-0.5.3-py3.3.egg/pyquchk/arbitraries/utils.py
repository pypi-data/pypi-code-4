""" Contain utility functions and decorators useful when defining custom
:class:`.Arbitrary` instances. Usually they haven't much use otherwise.
"""

from itertools import cycle, islice, count, product as product_
import random
from decorator import decorator
from six import PY3
from six.moves import zip_longest
from pyquchk.lazylist import LazyList

__all__ = ['roundrobin', 'interleave', 'product',
           'choice_weighted',
           'filter_possible', 'until_possible', 'unique']


@decorator
def filter_possible(method, self, *args, **kwargs):
    """ Decorator, when applied to a generator method (e.g. :meth:`.gen_serial`)
    filters generated values to keep only those for which :meth:`.could_generate`
    returns ``True``.
    """
    fails_cnt = 0
    for item in method(self, *args, **kwargs):
        if self.could_generate(item):
            yield item
            fails_cnt = 0
        else:
            fails_cnt += 1
            if fails_cnt > 10000:
                raise RuntimeError('Unable to satisfy could_generate after 10000 items from gen_serial in a %s instance.' % type(self).__name__)


@decorator
def until_possible(method, self, *args, **kwargs):
    """ Decorator, when applied to a method returning different values each time
    (e.g. :meth:`.next_random`) runs this method multiple times until a value
    for which :meth:`.could_generate` returns ``True`` is returned, and finally
    returns this value.
    """
    fails_cnt = 0
    func = lambda: method(self, *args, **kwargs)
    for item in iter(func, object()):
        if self.could_generate(item):
            return item
        else:
            fails_cnt += 1
            if fails_cnt > 10000:
                raise RuntimeError('Unable to satisfy could_generate after 10000 calls of next_random in a %s instance.' % type(self).__name__)


@decorator
def unique(method, self, *args):
    """ Decorator, when applied to a generator method (e.g. :meth:`.gen_serial`,
    :meth:`.shrink`) filters generated values to keep only unique values.
    For the :meth:`.shrink` method the value passed to the method is also
    considered.
    """
    seen = set()
    if 'shrink' in method.__name__:
        seen.add(args[0])

    for item in method(self, *args):
        if isinstance(item, list):
            s_item = tuple(item)
        elif isinstance(item, dict):
            s_item = tuple(item.items())
        else:
            s_item = item

        if s_item not in seen:
            yield item
            seen.add(s_item)


def roundrobin(iterables):
    """ Yield items from the given iterables in a round-robin fashion.

    What it does exactly is better explained with a simple example:

    .. ipython::

        >>> list(roundrobin(['ABC', 'D', 'EF']))
        ['A', 'D', 'E', 'B', 'F', 'C']

    :param iterables: List of finite or infinite iterables.
    """
    # Recipe credited to George Sakkis
    pending = len(iterables)
    iterators = (iter(it) for it in iterables)
    nexts = cycle(it.__next__ if PY3 else it.next for it in iterators)
    while pending:
        try:
            for next_f in nexts:
                yield next_f()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))


def interleave(xs, ys):
    """
    >>> list(interleave([], []))
    []
    >>> list(interleave([1], []))
    [1]
    >>> list(interleave([], ['a']))
    ['a']
    >>> list(interleave([1], ['a']))
    [1, 'a']
    >>> list(interleave([1, 2], ['a']))
    [1, 'a', 2]
    >>> list(interleave([1], ['a', 'b']))
    [1, 'a', 'b']
    >>> list(interleave([1, 2], ['a', 'b']))
    [1, 'a', 2, 'b']
    """
    for tup in zip_longest(xs, ys):
        for x in tup:
            if x is not None:
                yield x


def product(*iterables, **kwargs):
    """ product(*iterable, product=1)
    Cartesian product of all the iterables.

    Difference compared to the :func:`itertools.product` is that tuples are yield
    in the order suitable for infinite iterables (see examples below).

    Corner cases:

    .. ipython::

        >>> list(product([], []))
        []

        >>> list(product([1, 2, 3], []))
        []

        >>> list(product([], [1, 2, 3]))
        []

    2 iterables:

    .. ipython::

        >>> list(product([1], [1]))
        [(1, 1)]

        >>> list(product([1, 2], [1]))
        [(1, 1), (2, 1)]

        >>> list(product([1, 2], [1, 2]))
        [(1, 1), (1, 2), (2, 1), (2, 2)]

        >>> list(product([1, 2, 3], [1, 2, 3]))
        [(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (2, 3), (3, 1), (3, 2), (3, 3)]

        >>> list(product([1, 2, 3], [1, 2, 3])) == list(product([1, 2, 3], repeat=2))
        True

        >>> list(islice(product(count(1), count(1)), 1000)) == list(islice(product(count(1), repeat=2), 1000))
        True

        >>> infNN = product(count(1), count(1))

        >>> list(islice(infNN, 20))
        [(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (2, 3), (3, 1), (3, 2), (3, 3), (1, 4), (2, 4), (3, 4), (4, 1), (4, 2), (4, 3), (4, 4), (1, 5), (2, 5), (3, 5), (4, 5)]

        >>> lstNN = list(islice(infNN, 10000))

        >>> all(max(x) <= max(y) for x, y in zip(lstNN, lstNN[1:]))
        True

    3 iterables:

    .. ipython::

        >>> list(product([1, 2], [1, 2], [1, 2]))
        [(1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2), (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)]

        >>> len(list(product([1, 2, 3], [1, 2, 3], [1, 2, 3])))
        27

        >>> infNNN = product(count(1), count(1), count(1))
        >>> list(islice(infNNN, 20))
        [(1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2), (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2), (1, 1, 3), (1, 2, 3), (2, 1, 3), (2, 2, 3), (1, 3, 1), (1, 3, 2), (1, 3, 3), (2, 3, 1), (2, 3, 2), (2, 3, 3), (3, 1, 1), (3, 1, 2)]

        >>> lstNNN = list(islice(infNNN, 10000))
        >>> all(max(x) <= max(y) for x, y in zip(lstNNN, lstNNN[1:]))
        True
    """
    iterables = list(map(LazyList, iterables)) * kwargs.get('repeat', 1)

    for i in count():
        yielded_any = False

        for main_j, main_it in reversed(list(enumerate(iterables))):
            try:
                x = main_it[i]
            except IndexError:
                continue

            prod = product_(*[it[:i + 1 if j > main_j else i] for j, it in
                              enumerate(iterables) if j != main_j])

            for tup in prod:
                yield tup[:main_j] + (x,) + tup[main_j:]
                yielded_any = True

        if not yielded_any:
            break


def choice_weighted(elements):
    """ Like :func:`random.choice`, but the probability an item is chosen is
    proportional to its weight.

    For convenience, this function is available as ``random.choice_weighted``
    if you imported :mod:`.utils`.

    :param elements: list of tuples ``(item, weight)``, weight is any numeric value
    """
    rnd = random.random() * sum(w for _, w in elements)
    for el, w in elements:
        rnd -= w
        if rnd < 0:
            return el


random.choice_weighted = choice_weighted
