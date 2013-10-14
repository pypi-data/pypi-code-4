#!/usr/bin/env python

"""
Functions to utilize lists of Comparable objects.
"""


def find_equal(base, items):
    """Get an iterator of items equal to the base.

    @param base: base item to find equality
    @param items: list of items for comparison
    @return: generator of equal items
    """
    return (item for item in items if base.equality(item))


def match_equal(base, items):
    """Get the first item that is equivalent to the base.

    @param base: base item to find equality
    @param items: list of items for comparison
    @return: first equivalent item or None
    """
    for item in find_equal(base, items):
        return item

    return None


def find_similar(base, items):
    """Get an iterator of items similar to the base.

    @param base: base item to locate best match
    @param items: list of items for comparison
    @return: generator of similar items
    """
    return (item for item in items if base.similarity(item))


def match_similar(base, items):
    """Get the most similar matching item from a list of items.

    @param base: base item to locate best match
    @param items: list of items for comparison
    @return: most similar matching item or None
    """
    finds = list(find_similar(base, items))
    if finds:
        return max(finds, key=base.similarity)  # TODO: make O(n)

    return None


def duplicates(base, items):
    """Get an iterator of items similar but not equal to the base.

    @param base: base item to perform comparison against
    @param items: list of items to compare to the base
    @return: generator of items sorted by similarity to the base
    """
    for item in items:
        if item.similarity(base) and not item.equality(base):
            yield item


def sort(base, items):
    """Get a sorted list of items ranked in descending similarity.

    @param base: base item to perform comparison against
    @param items: list of items to compare to the base
    @return: list of items sorted by similarity to the base
    """
    return sorted(items, key=base.similarity, reverse=True)
