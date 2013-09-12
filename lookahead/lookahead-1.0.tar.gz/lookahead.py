# -*- coding: utf-8 -*-
# Copyright © 2013 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

VERSION = (1,0,0, 'final', 0)

def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%spre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = "%s%s" % (version, VERSION[3])
            if VERSION[4] != 0:
                version = '%s%s' % (version, VERSION[4])
    return version

def lookahead(iterable, *args, **kwargs):
    """Constructs a generator over the iterable yielding look-ahead (and/or
    “look-behind”) tuples. One tuple will be generated for each element value
    accessible from the iterator, containing that element and the number of
    elements specified just prior to and immediately after. When no such
    element exists, the None is used instead.

    If one were to think of iterator as a list, this is would be similar to
    appending [None]*lookahead and prepending [None]*lookbehind, then
    iterating over and returning a sliding window of length lookbehind+1+
    lookahead (except of course that instead of generating the such a list,
    this implementation generates (and caches) lookahead values only as
    needed).

    lookahead() may be called with 1, 2, or 3 parameters:

        lookahead(iterable)
            Defaults to lookahead=1, lookbehind=0
        lookahead(iterable, lookahead)
            Defaults to lookbehind=0
        lookahead(iterable, lookbehind, lookahead)
            Notice that lookahead is now the 3rd parameter!

    Example semantics:

        lookahead(iterable):
            yield (item, next)
        lookahead(iterable, 2):
            yield (item, next, next+1)
        lookahead(iterable, 1, 2):
            yield (prev, item, next, next+1)
        lookahead(iterable, p, n):
            yeild (prev, ..., prev+p-1, item, next, ..., next+n-1)
    """
    # Deal with our funny parameter handling (2 optional positional
    # parameters, with the *2nd* optional parameter taking precendence
    # if only one is specified):
    if   len(args) == 0: num_prev, num_next = 0, 1
    elif len(args) == 1: num_prev, num_next = 0, args[0]
    elif len(args) == 2: num_prev, num_next = args[0], args[1]
    else: raise TypeError("%s() takes 1, 2, or 3 arguments (%d given)"
                          % (lookahead.__name__, len(args)))

    # Construct an iterator over iterable (has no effect if it is
    # already iterable):
    iterator = iter(iterable)

    # Set the lookbehind positions to None and generate the first element.
    # This will immediately raise StopIteration in the trivial case:
    lst = [None]*num_prev + [iterator.next()]

    # Prime the needed lookahead values:
    for x in xrange(num_next):
        try:
            lst.append(iterator.next())
        except StopIteration:
            lst.append(None)
            num_next -= 1

    # Yield the current tuple, then shift the list and generate a new item:
    for item in iterator:
        yield tuple(lst)
        lst = lst[1:] + [item]

    # Yield the last full tuple, then continue with None for each lookahead
    # position:
    for x in xrange(num_next+1):
        yield tuple(lst)
        lst = lst[1:] + [None]

    # Done!
    raise StopIteration
