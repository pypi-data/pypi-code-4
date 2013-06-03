# -*- coding: utf-8 -*-

# imports
import cherrypy

FORBIDDEN_PHRASES = ['drop ', 'select ', 'dump ', 'insert ', 'delete ', 'update ',
                     'drop\\ ', 'select\\ ', 'dump\\ ', 'insert\\ ', 'delete\\ ', 'update\\ ']
FORBIDDEN_CHARS = ['´', '`']

def insertion_safe(*args, **kwargs):
    for arg in list(args) + kwargs.values():
        if isinstance(arg, dict):
            arg = arg.keys()
        if not isinstance(arg, list):
            arg = [arg]
        for elem in arg:
            elem = str(elem)
            # 1. check: forbidden phrases
            for phrase in FORBIDDEN_PHRASES:
                if elem.lower().find(phrase) >= 0:
                    return False, elem
            # 2. check: forbidden chars
            for char in FORBIDDEN_CHARS:
                if elem.lower().find(char) >= 0:
                    return False, elem
    return True, None