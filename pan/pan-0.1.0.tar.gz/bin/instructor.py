#!/usr/bin/python

"""
Hide anything in a Div with class 'instructor' unless
an instructor variable is set in the document.
"""

from pan.pandoc import toJSONFilter


def checkmetabool(meta, key):
    ob = meta.get(key, None)
    return ob and ob.get('MetaBool', None)


def instructor(key, value, format, **meta):

    if not key == 'Div':
        return

    if checkmetabool(meta, 'instructor'):
        return None

    [[ident, classes, keyvals], content] = value

    if set(["instructor", "answer"]).intersection(set(classes)):
        return []


if __name__ == "__main__":
    toJSONFilter(instructor)
