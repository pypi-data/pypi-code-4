# Module:   stat
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""stat"""


def minmax(xs):
    """Return the min and max values for the given iterable

    :param xs: An iterable of values
    :type xs: Any iterable of single numerical values.

    This function returns both the min and max of the given iterable
    by computing both at once and iterating/consuming the iterable once.
    """

    it = iter(xs)
    x = next(it)
    _min, _max = x, x
    for x in it:
        if x < _min:
            _min = x
        if x > _max:
            _max = x
    return _min, _max,


__all__ = ("minmax",)
