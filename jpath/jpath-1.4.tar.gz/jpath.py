#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Access nested dicts and lists using JSON-like path notation.

Note that this code is written for python 3.

The notation is as follows:

    You can just write the names of components in your path like you
    would in javascript:

    foo.bar.baz

    To access arrays or names with spaces in them, use the '[]' notation.
    You can use negative indices with arrays to count from the end.

    ["foo"]["bar"]["baz"]
    array[-1].attr
    [3]

    You can use the wildcard character '*' to iterate over all elements:

    foo.*.baz
    ["foo"][*]["baz"]

    This may return more or less than a single element. Use get to get the
    first one, and get_all to get a list of all possibilities.
    If you want to skip any number of elements in path, use two dots '..':

    foo..baz

    You can slice the arrays just like in python:

    array[1:-1:2]

    Finally, you can filter the elements:

    foo(bar.baz=true)
    foo.bar(baz>0).baz
    foo(bar="yawn").bar

    At the moment only =, >, <, >=, <= and != operators are available,
    and you can only use them with strings, integers and boolean values.

This code was written in STX Next.
"""

# We use very simple top-down parsing using recursive function calls.
# This may break in python for very very very long jpaths.


import re
import operator

__all__ = ['get', 'get_all']
__version__ = '1.4'


# Make it work both in python 2.x and 3.x
try:
    basestring
except NameError:
    basestring = str


def _pop_token(tokens):
    try:
        token = tokens.pop()
    except IndexError:
        token = NoneToken()
    return token


class Tokenizer:
    # list of all token classes marked with @Tokenizer.token
    tokens = {}

    def __init__(self):
        self.tokens_re = re.compile(r'|'.join(
            r'(?P<{0}>{1})'.format(token.name, token.regexp)
            for token in sorted(self.tokens.values(),
                                key=operator.attrgetter("priority"))
        ))

    @classmethod
    def token(cls, token_class):
        """Marks a token class to be used in tokenizer."""

        cls.tokens[token_class.name] = token_class
        return cls

    def tokenize(self, jpath):
        """
        Breaks a string into tokens.

        >>> [(t.name, t.value) for t in TOKENIZER.tokenize("ziew")]
        [('fragment', 'ziew')]
        >>> [(t.name, t.value) for t in TOKENIZER.tokenize("ziew.yawn")]
        [('fragment', 'ziew'), ('fragment', 'yawn')]
        >>> [(t.name, t.value) for t in TOKENIZER.tokenize('ziew["yawn"]')]
        [('fragment', 'ziew'), ('element', 'yawn')]
        >>> [(t.name, t.value) for t in TOKENIZER.tokenize('ziew[0]')]
        [('fragment', 'ziew'), ('index', 0)]
        >>> [(t.name, t.value) for t in TOKENIZER.tokenize("ziew.yawn+")]
        [('fragment', 'ziew'), ('fragment', 'yawn'), ('error', '+')]
        """

        for match in self.tokens_re.finditer(jpath):
            name = match.lastgroup
            if match.group(name):
                params = dict(p for p in match.groupdict().items()
                              if p[1] is not None)
                yield self.tokens[name](**params)


class Token:
    """Base class for tokens."""

    @staticmethod
    def apply(tokens, data):
        token = _pop_token(tokens)
        for value in token.parse(tokens, data):
            yield value

    def parse(self, tokens, data):
        """
        Default parsing method for most tokens: parse the subtree
        under token's value in data.
        """

        return Token.apply(tokens, data[self.value])


@Tokenizer.token
class FragmentToken(Token):
    """foo.bar.baz"""

    regexp = r'(^|(?<=\.\.)|\.)(?P<fragment_name>[a-zA-Z0-9_]+)'
    name = 'fragment'
    priority = 50

    def __init__(self, fragment, fragment_name):
        self.value = fragment_name


@Tokenizer.token
class ElementToken(Token):
    """["foo"]["bar"]["baz"], with quote escaping"""

    regexp = r'\["(?P<element_name>([^"]|\\")*)"\]'
    name = 'element'
    priority = 50

    def __init__(self, element, element_name):
        """
        >>> ElementToken(r'["ziew"]', r'ziew').value
        'ziew'
        >>> ElementToken('[r'["\"quotes\""]', r'\"quotes\"').value
        '"quotes"'
        """

        # Un-escape escaped double quotes.
        self.value = element_name.replace(r'\"', '"')


@Tokenizer.token
class IndexToken(Token):
    """[0][1][-1]"""

    regexp = r'\[(?P<index_value>-?[0-9]+)\]'
    name = 'index'
    priority = 50

    def __init__(self, index, index_value):
        self.value = int(index_value)


@Tokenizer.token
class SliceToken(Token):
    """[0:-1:2], may return multiple results"""

    regexp = (r'\[(?P<slice_start>-?[0-9]+)?:(?P<slice_end>-?[0-9]+)?'
              r'(:(?P<slice_step>-?[0-9]+))?\]')
    name = '_slice'
    priority = 50

    def __init__(self, _slice, slice_start=None, slice_end=None,
                 slice_step=None):
        self.start = int(slice_start) if slice_start is not None else None
        self.end = int(slice_end) if slice_end is not None else None
        self.step = int(slice_step) if slice_step is not None else None

    def parse(self, tokens, data):
        for item in data[self.start:self.end:self.step]:
            for value in Token.apply(list(tokens), item):
                yield value


@Tokenizer.token
class FilterToken(Token):
    """(foo=3)"""

    regexp = (r'[(](?P<filter_path>[^(<=>)!]+)'
              r'\s*(?P<filter_operator>[<=>]|>=|<=|!=|==)\s*'
              r'(?P<filter_value>"([^"]|\\")*"|-?[0-9]|true|false)[)]')
    name = '_filter'
    priority = 50
    op = {
        '=': operator.eq,
        '>': operator.gt,
        '<': operator.lt,
        '!=': operator.ne,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq
    }

    def __init__(self, _filter, filter_path, filter_operator,  filter_value):
        """
        >>> FilterToken(r'(foo="b\"ar")', r'foo', r'=', r'"b\"ar"').value
        'b"ar'
        >>> FilterToken(r'(bar=-1)', r'bar', r'=', r'-1').value
        -1
        """
        self.path = filter_path
        if filter_value.startswith('"'):
            self.value = filter_value[1:-1].replace(r'\"', '"')
        elif filter_value in ('true', 'false'):
            self.value = filter_value == 'true'
        else:
            self.value = int(filter_value)
        self.operator = filter_operator

    def parse(self, tokens, data):
        token = _pop_token(tokens)
        try:
            # If it's a dict, iterate over values, not keys.
            data = data.values()
        except AttributeError:
            pass
        for item in data:
            try:
                item_value = get(self.path, item)
            except (TypeError, IndexError, KeyError):
                # Skip the branches that don't have the value we look for.
                continue
            if self.op[self.operator](item_value, self.value):
                    for value in token.parse(tokens, item):
                        yield value

@Tokenizer.token
class WildcardToken(Token):
    """*[*].*, may return multiple results"""

    regexp = r'(^|(?<=\.\.)|\.)\*|\[\*\]'
    name = 'wildcard'
    priority = 50

    def __init__(self, wildcard):
        self.value = None

    def parse(self, tokens, data):
        token = _pop_token(tokens)
        try:
            # If it's a dict, iterate over values, not keys.
            data = data.values()
        except AttributeError:
            pass
        for item in data:
            try:
                for value in token.parse(list(tokens), item):
                    yield value
            except (TypeError, IndexError, KeyError):
                # Ignore errors inside branches, because some
                # of the branches may have different structure
                # than our jpath wants.
                pass


@Tokenizer.token
class EllipsisToken(Token):
    """.., may return multiple results"""

    regexp = r'\.\.'
    name = 'ellipsis'
    priority = 60

    def __init__(self, ellipsis):
        self.value = None

    def parse(self, tokens, data):
        def dive(data):
            yield data
            stack = [data]
            while stack:
                data = stack.pop()
                try:
                    # If it's a dict, iterate over values, not keys.
                    data = data.values()
                except AttributeError:
                    pass
                orig_data = data
                try:
                    # Skip non-iterable datatypes.
                    data = iter(data)
                except TypeError:
                    continue
                for item in data:
                    if isinstance(item, basestring):
                        # Strings are nasty, because they can be iterated
                        # recursively idefinitely.
                        continue
                    if item is orig_data:
                        # We are iterating over something that behaves like
                        # the strings, refuse to descend.
                        break
                    stack.append(item)
                    yield item
        token = _pop_token(tokens)
        for item in dive(data):
            try:
                for value in token.parse(list(tokens), item):
                    yield value
            except (TypeError, IndexError, KeyError):
                # Ignore errors inside branches, because some
                # of the branches may have different structure
                # than our jpath wants.
                pass


@Tokenizer.token
class ErrorToken(Token):
    """Catchall for everything that didn't match other tokens."""

    regexp = r'.*'
    name = 'error'
    priority = 100

    def __init__(self, error):
        self.value = error

    def parse(self, tokens, data):
        raise SyntaxError("Unexpexted '{0}' in jpath.".format(self.value))
        yield None


class NoneToken(Token):
    """Special token for marking lack of tokens."""

    def parse(self, tokens, data):
        yield data


# We only ever need one tokenizer
TOKENIZER = Tokenizer()


def get_all(jpath, data):
    """
    Get list of all elements matched by given jpath in the data datastructure.

    >>> get_all('', 1)
    [1]
    >>> get_all('[1]', [1, 2])
    [2]
    >>> get_all('[*]', [1, 2])
    [1, 2]
    >>> get_all('*', [1, 2])
    [1, 2]
    >>> get_all('*[0]', [1, [2, 4], 3])
    [2]
    >>> get_all('*[0]', [1, [2, 4], 3, []])
    [2]
    >>> get_all('*.ziew', [1, {'ziew':2}, [3], []])
    [2]
    >>> get_all('..ziew', [1, 'ziew', {'ziew': 3, 'yawn': [{'ziew': 4}]}])
    [3, 4]
    >>> get_all('a.b', {'a': {'b': 3, 'c': {'b': 4}}})
    [3]
    >>> get_all('a..b', {'a': {'b': 3, 'c': {'b': 4}}})
    [3, 4]
    >>> get_all('[1:]', [1, 2, 3])
    [2, 3]
    >>> get_all('[:-1]', [1, 2, 3])
    [1, 2]
    >>> get_all('[::2]', [1, 2, 3, 4])
    [1, 3]
    >>> get_all('(x=1).y', [{'x':1, 'y':2}, {'x':0, 'y':3}, {'x':1, 'y':4}])
    [2, 4]
    >>> get_all('(x>0).y', [{'x':1, 'y':2}, {'x':0, 'y':3}, {'x':1, 'y':4}])
    [2, 4]
    >>> get_all('..', {'a':1, 'x':[2], 'c':[{'b': '3'}]})
    [{'a': 1, 'x': [2], 'c': [{'b': '3'}]}, 1, [2], [{'b': '3'}], {'b': '3'}, 2]
    >>> get_all('a[*].b.c', {'a': [{'b': {'c': 0}}, {'b': {'c': 1}}]})
    [0, 1]
    """

    tokens = list(TOKENIZER.tokenize(jpath))
    # Popping from the end of the list is faster.
    tokens.reverse()
    return list(Token.apply(tokens, data))


def get(jpath, data):
    """
    Get the first element matched by given jpath in the data datastructure.

    >>> get('', 3)
    3
    >>> get('ziew', {"ziew": 3})
    3
    >>> get('ziew.yawn', {"ziew": {"yawn": 3}})
    3
    >>> get('ziew["yawn"]', {"ziew": {"yawn": 3}})
    3
    >>> get('ziew[2]', {"ziew": [1, 2, 3]})
    3
    >>> get('[2]', [1, 2, 3])
    3
    >>> get('[*]', [1, 2, 3])
    1
    """

    return get_all(jpath, data)[0]

if __name__ == "__main__":
    # Run tests when started.
    import doctest
    doctest.testmod()
