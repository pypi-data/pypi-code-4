
def reverse_dict(d):
    """ Reverses direction of dependence dict

    >>> reverse_dict({'a': {1, 2}, 'b': {2, 3}, 'c':set()})
    {1: {'a'}, 2: {'a', 'b'}, 3: {'b'}}
    """
    result = {}
    for key in d:
        for val in d[key]:
            if val not in result:
                result[val] = set()
            result[val].add(key)
    return result

def key_to_cmp(key):
    """ Convert a key to a comparator function """
    def key_cmp(a, b):
        return cmp(key(a), key(b))
    return key_cmp

