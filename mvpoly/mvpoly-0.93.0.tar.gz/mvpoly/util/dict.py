import itertools as its
import mvpoly.util.common

def merge_dicts(d1, d2, merge):
    """
    Merges two dictionaries, non-destructively, combining 
    values on duplicate keys as defined by the final *merge*
    argument.

    This function is a modified version of an answer to a 
    `Stack Overflow question <http://stackoverflow.com/questions/38987/>`_
    by rcreswick.
    """
    result = dict(d1)
    for k, v in d2.iteritems():
        result[k] = merge(result[k], v) if k in result else v

    return result

def merge_dicts_nonzero(d1, d2, merge):
    """
    As :meth:`merge_dicts`, but not inserting into the results
    dictionary those item that would have a zero value.
    """
    k1s = set(d1.keys())
    k2s = set(d2.keys())

    p1s = ( (k, merge(d1[k], 0)) for k in (k1s - k2s) )
    p2s = ( (k, merge(0, d2[k])) for k in (k2s - k1s) )
    ips = ( (k, merge(d1[k], d2[k])) for k in (k1s & k2s) )
    izs = ( (k, v) for (k, v) in ips if v != 0 )

    return dict( its.chain(p1s, p2s, izs) )

def sum(d1, d2) :
    """
    Return the sum of dictionaries with items with 
    zero values removed.
    """
    return merge_dicts_nonzero(d1, d2, lambda x, y : x + y)

def negate(d) :
    """
    Return the dictionary that is its argument, but with the values
    negated.
    """
    return dict((k, -v) for (k, v) in d.items())
