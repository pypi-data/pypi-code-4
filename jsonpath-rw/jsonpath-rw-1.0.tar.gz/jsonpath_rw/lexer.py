from __future__ import unicode_literals, print_function, absolute_import, division, generators, nested_scopes
import sys
import logging

import ply.lex

logger = logging.getLogger(__name__)

class JsonPathLexer(object):
    '''
    A Lexical analyzer for JsonPath. 
    '''
    
    def __init__(self, debug=False):
        self.debug = debug

    def tokenize(self, string):
        '''
        Maps a string to an iterator over tokens. In other words: [char] -> [token]
        '''
        
        new_lexer = ply.lex.lex(module=self, debug=self.debug, errorlog=logger)
        new_lexer.latest_newline = 0
        new_lexer.input(string)

        while True:
            t = new_lexer.token()
            if t is None: break
            t.col = t.lexpos - new_lexer.latest_newline
            yield t

    # ============== PLY Lexer specification ==================
    #
    # This probably should be private but:
    #   - the parser requires access to `tokens` (perhaps they should be defined in a third, shared dependency)
    #   - things like `literals` might be a legitimate part of the public interface.
    #
    # Anyhow, it is pythonic to give some rope to hang oneself with :-)

    literals = ['*', '.', '[', ']', '(', ')', '$', ',', ':', '|', '&', '@']
    
    reserved_words = { 'where': 'WHERE' }

    tokens = ['DOUBLEDOT', 'NUMBER', 'ID'] + list(reserved_words.values())

    states = [ ('singlequote', 'exclusive'),
               ('doublequote', 'exclusive') ]

    # Normal lexing, rather easy
    t_DOUBLEDOT = r'\.\.'
    t_ignore = ' \t'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved_words.get(t.value, 'ID')
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Single-quoted strings
    t_singlequote_ignore = ''
    def t_SINGLEQUOTE(self, t):
        r'\''
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.push_state('singlequote')

    def t_singlequote_SINGLEQUOTE(self, t):
        r"([^']|\\')*'"
        t.value = t.value[:-1]
        t.type = 'ID'
        t.lexer.pop_state()
        return t

    def t_singlequote_error(self, t):
        raise Exception('Error on line %s, col %s while lexing singlequoted field: Unexpected character: %s ' % (t.lexer.lineno, t.lexpos - t.latest_newline, t.value[0]))


    # Double-quoted strings
    t_doublequote_ignore = ''
    def t_DOUBLEQUOTE(self, t):
        r'"'
        t.lexer.string_start = t.lexer.lexpos
        t.lexer.push_state('doublequote')

    def t_doublequote_DOUBLEQUOTE(self, t):
        r'([^"]|\\")*"'
        t.value = t.value[:-1]
        t.type = 'ID'
        t.lexer.pop_state()
        return t

    def t_doublequote_error(self, t):
        raise Exception('Error on line %s, col %s while lexing doublequoted field: Unexpected character: %s ' % (t.lexer.lineno, t.lexpos - t.latest_newline, t.value[0]))

    # Counting lines, handling errors
    def t_newline(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.latest_newline = t.lexpos

    def t_error(self, t):
        raise Exception('Error on line %s, col %s: Unexpected character: %s ' % (t.lexer.lineno, t.lexpos - t.latest_newline, t.value[0]))

if __name__ == '__main__':
    logging.basicConfig()
    lexer = JsonPathLexer(debug=True)
    for token in lexer.tokenize(sys.stdin.read()):
        print('%-20s%s' % (token.value, token.type))
