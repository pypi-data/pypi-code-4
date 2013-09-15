""" Contain utility functions and decorators useful when defining custom
:class:`.Arbitrary` instances. Usually they haven't much use otherwise.
"""

from itertools import cycle, islice
import random
from decorator import decorator
from six import PY3

__all__ = ['roundrobin', 'choice_weighted',
           'filter_possible', 'until_possible',
           'unique']


@decorator
def filter_possible(method, self, *args, **kwargs):
    """ Decorator, when applied to a generator method (e.g. :meth:`.gen_serial`)
    filters generated values to keep only those for which :meth:`.could_generate`
    returns ``True``.
    """
    for item in method(self, *args, **kwargs):
        if self.could_generate(item):
            yield item


@decorator
def until_possible(method, self, *args, **kwargs):
    """ Decorator, when applied to a method returning different values each time
    (e.g. :meth:`.next_random`) runs this method multiple times until a value
    for which :meth:`.could_generate` returns ``True`` is returned, and finally
    returns this value.
    """
    func = lambda: method(self, *args, **kwargs)
    for item in iter(func, object()):
        if self.could_generate(item):
            return item


@decorator
def unique(method, self, x):
    """ Decorator, when applied to a generator method (e.g. :meth:`.gen_serial`,
    :meth:`.shrink`) filters generated values to keep only unique values.
    For the :meth:`.shrink` method the value passed to the method is also
    considered.
    """
    seen = set()
    if 'shrink' in method.__name__:
        seen.add(x)

    for item in method(self, x):
        if isinstance(item, list):
            s_item = tuple(item)
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
