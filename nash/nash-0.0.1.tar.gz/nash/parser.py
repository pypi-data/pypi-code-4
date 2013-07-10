import ply.yacc as yacc
from . import lexer as lexer

class Parser(lexer.Lexer):
    def __init__(self):
        super(Parser, self).__init__()
        yacc.yacc(module=self)

    precedence = ( ('left', 'ADD')
                 , ('left', 'MULTIPLY')
                 )

    def p_expression_integer(self, p):
        'expression : INTEGER'
        p[0] = ('INTEGER', p[1])

    def p_expression_parnethesis(self, p):
        'expression : LEFT_PAREN expression RIGHT_PAREN'
        p[0] = p[2]

    def p_expression_float(self, p):
        'expression : FLOAT'
        p[0] = ('FLOAT', p[1])

    def p_expression_add(self, p):
        'expression : expression ADD expression'
        if p[2] == '+':
          p[0] = ('ADD', p[1], p[3])
        else:
          p[0] = ('SUBTRACT', p[1], p[3])

    def p_expression_multiply(self, p):
        'expression : expression MULTIPLY expression'
        if p[2] == '*':
          p[0] = ('MULTIPLY', p[1], p[3])
        else:
          p[0] = ('DIVIDE', p[1], p[3])

    def parse(self, program):
        return yacc.parse(program)
