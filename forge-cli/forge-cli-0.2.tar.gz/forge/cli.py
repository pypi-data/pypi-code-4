# -*- coding: utf-8 -*-

"""
forge.cli
~~~~~~~~~~~~~

this are helpers utilities for cli output.


from::
 https://github.com/kennethreitz/clint
 https://pypi.python.org/pypi/colorama


embeded as this project requires no dependencies

"""

from __future__ import absolute_import

import re
import sys


CSI = '\033['


def code_to_chars(code):
    return CSI + str(code) + 'm'


class AnsiCodes(object):
    def __init__(self, codes):
        for name in dir(codes):
            if not name.startswith('_'):
                value = getattr(codes, name)
                setattr(self, name, code_to_chars(value))


class AnsiFore:
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    RESET = 39


FORE = AnsiCodes(AnsiFore)

DISABLE_COLOR = False


class ColoredString(object):
    """Enhanced string for __len__ operations on Colored output."""

    def __init__(self, color, s):
        super(ColoredString, self).__init__()
        self.s = s
        self.color = color

    def __getattr__(self, att):
        def func_help(*args, **kwargs):
            result = getattr(self.s, att)(*args, **kwargs)
            if isinstance(result, basestring):
                return self._new(result)
            elif isinstance(result, list):
                return [self._new(x) for x in result]
            else:
                return result

        return func_help

    @property
    def color_str(self):
        if sys.stdout.isatty() and not DISABLE_COLOR:
            return '%s%s%s' % (
                getattr(FORE, self.color), self.s, FORE.RESET)
        else:
            return self.s

    def __len__(self):
        return len(self.s)

    def __repr__(self):
        return "<%s-string: '%s'>" % (self.color, self.s)

    def __unicode__(self):
        value = self.color_str
        if isinstance(value, bytes):
            return value.decode('utf8')
        return value

    def __str__(self):
        return unicode(self).encode('utf8')

    def __iter__(self):
        return iter(self.color_str)

    def __add__(self, other):
        return str(self.color_str) + str(other)

    def __radd__(self, other):
        return str(other) + str(self.color_str)

    def __mul__(self, other):
        return (self.color_str * other)

    def _new(self, s):
        return ColoredString(self.color, s)


def clean(s):
    strip = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")
    txt = strip.sub('', str(s))

    strip = re.compile(r'\[\d+m')
    txt = strip.sub('', txt)

    return txt


def black(string):
    return ColoredString('BLACK', string)


def red(string):
    return ColoredString('RED', string)


def green(string):
    return ColoredString('GREEN', string)


def yellow(string):
    return ColoredString('YELLOW', string)


def blue(string):
    return ColoredString('BLUE', string)


def magenta(string):
    return ColoredString('MAGENTA', string)


def cyan(string):
    return ColoredString('CYAN', string)


def white(string):
    return ColoredString('WHITE', string)


def disable():
    """Disables colors."""
    global DISABLE_COLOR

    DISABLE_COLOR = True
