# coding: utf-8


import re
import sys

def read_name(s):
    match = re.match(r'\s*(?P<name>[^=]+?)\s*(?P<rest>=([\n]|.)*)', s)
    return match.group('name'), match.group('rest')


def read_value(s):
    match = re.match(r'=\s*(?P<val>"([^\\"]|\\.)*?"|(\\.|[^,=\n+<>#;])*)\s*(?P<rest>([\n]|.)*)', s)
    return match.group('val'), match.group('rest')


def read_extra(s):
    match = re.match(r'\s*\+\s*(?P<rest>([\n]|.)*)', s)
    if match:
        return read_pair(match.group('rest'))
    else:
        return [], s


def read_pair(s):
    name, rest = read_name(s)
    val, rest = read_value(rest)
    extra, rest = read_extra(rest)
    extra.insert(0, (name, val))
    return extra, rest


def read_rdn(s, flat=True):
    if not(s.strip()):
        return []
    p, rest = read_pair(s)
    match = re.match(r'\s*[,;]\s*(?P<rest>([\n]|.)*)', rest)
    if match:
        extra = read_rdn(match.group('rest'))
    else:
        extra = []
    if flat:
        p.extend(extra)
        return p
    extra.insert(0, p)
    return extra

class RDN(dict):
    """Объектно-ориентированная обертка вокруг парсера РДН"""

    def __init__(self, s):
        """Превращает строку в формате RDN в словарь

        :s: исходная строка

        """
        super(RDN, self).__init__(read_rdn(s))
