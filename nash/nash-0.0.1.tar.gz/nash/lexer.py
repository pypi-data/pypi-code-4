from collections import namedtuple
from ply import lex

class Lexer(object):
    def __init__(self):
        self._input = None
        self.lexer = lex.lex(module=self)

    tokens = ('INTEGER'
             , 'FLOAT'
             , 'ADD'
             , 'MULTIPLY'
             , 'LEFT_PAREN'
             , 'RIGHT_PAREN'
             )

    t_ADD         = r'\+|-'
    t_MULTIPLY    = '\*|/'
    t_LEFT_PAREN  = r'\('
    t_RIGHT_PAREN = r'\)'

    def t_FLOAT(self, t):
        r'-?[0-9]*\.[0-9]+'
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r'-?[0-9]+'
        t.value = int(t.value)
        return t

    t_ignore  = ' \t'

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def token(self):
        return self.lexer.token()

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self._input = value
        self.lexer.input(self._input)
