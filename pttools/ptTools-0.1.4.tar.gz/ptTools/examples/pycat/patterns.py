#!/usr/bin/env python3

"""Patterns for pycat.py."""

import symbol
from symbol import *
import token
import keyword

import ptTools

from ptTools.ptpatterns import AnyPattern
from ptTools.ptpatterns import ConcatenationPattern as Con
from ptTools.ptpatterns import LiteralPattern as Lit
from ptTools.ptpatterns import UnionPattern as Opt
from ptTools.ptpatterns import TestPattern as Test
from ptTools.ptpatterns import TuplePattern as Tup
from ptTools.ptpatterns import TerminalPattern as Terminal
from ptTools.ptpatterns import _
from ptTools.ptpatterns import more
from ptTools.ptpatterns import prettyprint, prettyinput

from ptTools.examples.pycat.styles import style_node as style
from ptTools.examples.pycat.styles import style_depth
from ptTools.examples.pycat.styles import style_token


class CallableAnyTokenPattern(AnyPattern):    
    def __call__(self, arg):
        return Tup(_, _%style(arg))

def pdebug(node):
    import pdb; pdb.set_trace()

anytoken = CallableAnyTokenPattern()
debug = style('debug')

## The following patterns are defined here, for later reuse.
## TODO - Use a to be created TerminalPattern class.
NAME    = Tup(token.NAME, _)
NUMBER  = Tup(token.NUMBER, _)
STRING  = Tup(token.STRING, _)
NEWLINE = Tup(token.NEWLINE, Lit(''))
KEYWORD = Tup(token.NAME, Test(lambda n : keyword.iskeyword(n.string)))
IMPORT  = Tup(token.NAME, Lit('import'))
SELF    = Tup(token.NAME, Lit('self'))
SUPER   = Tup(token.NAME, Lit('super'))
CLASS   = Tup(token.NAME, Lit('class'))
DEF     = Tup(token.NAME, Lit('def'))
RAISE   = Tup(token.NAME, Lit('raise'))
BOOL    = Opt('False', 'True', 'None')
OP      = Tup(Test(lambda n : token.LPAR<= n <=token.OP), _)
BOOLOP  = Opt('and', 'or', 'not')
PAREN   = Opt('(',')')
BRACE   = Opt('{','}')
SQB     = Opt('[',']')
COMMA   = Tup(token.COMMA, _)


## The actual pattern definition:

node_patterns = [

    ## Primitives:
    NUMBER  % style('number'),
    STRING  % style('string'),
    ## Keywords:
    KEYWORD % style('keyword'),
    SELF    % style('self'),
    SUPER   % style('super'),
    BOOL    % style('bool'),
    ## Operators:
    OP      % style('op'),
    BOOLOP  % style('boolop'),
    PAREN   % style('paren')   % style_depth,
    BRACE   % style('brace')   % style_depth,
    SQB     % style('bracket') % style_depth,

    ##
    ## file_input    ::= (NEWLINE | stmt)* ENDMARKER
    Tup(Lit(file_input) >> STRING % style('mod_comment'), more),

    ##
    ## raise_stmt    ::= 'raise' [test ['from' test]]
    Tup(raise_stmt,
        RAISE % style('raise'),
        [ Tup(Lit(test) >> Tup(power,
                               Tup(atom, NAME % style('raised_name')),
                               +(Tup(trailer, '(', more) ## ignore
                                 | Tup(_, more % style('raised_name'))))) ]),

    ##
    ## funcdef       ::= 'def' NAME parameters ['->' test] ':' suite
    ## parameters    ::= '(' [typedargslist] ')'    
    ## typedargslist ::= (tfpdef ['=' test] (',' tfpdef ['=' test])*
    ##                    [ ',' ['*' [tfpdef] (',' tfpdef ['=' test])*
    ##                      [',' '**' tfpdef] | '**' tfpdef]]
    ##                    | '*' [tfpdef] (',' tfpdef ['=' test])*
    ##                      [',' '**' tfpdef] | '**' tfpdef)    
    Tup(funcdef,
        DEF % style('def'),
        NAME % style('def_name'),
        Tup(parameters,
            '(',
            [ Tup(typedargslist, more % style('parameter')) ],
            ')' ),
        ':',
        Tup(suite,
            NEWLINE,
            _,
            [ Tup(Lit(stmt) >> Tup(token.STRING,
                                   _ % style('def_comment'),
                                   more)) ],
         more)),

    ##
    ## self as parameter:
    Tup(tfpdef,
        (token.NAME, Lit('self') % style('self'))),

    ##
    ## decorator    ::= '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
    Tup(decorator,
        anytoken('decorator')*2,
        more),

    ##
    ## classdef     ::= 'class' NAME ['(' [arglist] ')'] ':' suite
    ## arglist      ::= (argument ',')* (argument [',']
    ##                                   |'*' test (',' argument)* [',' '**' test] 
    ##                                   |'**' test)
    ## suite        ::= simple_stmt | NEWLINE INDENT stmt+ DEDENT
    ##
    ## Optional kwargs are not included in the following pattern:
    Tup(classdef,
        CLASS % style('class'),
        NAME % style('class_name'),
        [ '(',
          [ Tup(arglist,
                +Con(
                    Tup(Lit(argument) >> Tup(power, more % style('arglist'))),
                    [','])) ],
          ')' ],
        ':',
        Tup(suite,
            [ NEWLINE ],
            _,
            [ Tup(Lit(stmt) >> Tup(token.STRING,
                                   _ % style('class_comment'),
                                   more)) ],
            more)),

    ##
    ## import_stmt  ::= import_name | import_from
    ## import_name  ::= 'import' dotted_as_names
    ## import_from  ::= ('from' (('.' | '...')* dotted_name | ('.' | '...')+)
    ##                   'import' ('*' | '(' import_as_names ')' | import_as_names))
    ## import_as_name ::= NAME ['as' NAME]
    ## dotted_as_name ::= dotted_name ['as' NAME]
    ## Relative imports are not caught by the following pattern:
    Tup(import_stmt,
        Tup(import_name,
            IMPORT % style('import'),
            Tup(dotted_as_names,
                +Con(Tup(dotted_as_name,
                         Tup(dotted_name, more) % style('imported_name'),
                         ['as', _ % style('imported_name') ]),
                     [ ',' ])))
        | Tup(import_from,
              'from',
              Tup(dotted_name, more) % style('imported_name'),
              'import',
              Tup(import_as_names,
                  +Con(Tup(Lit(import_as_name) >>
                           NAME % style('imported_name'),
                           [ 'as', NAME % style('imported_name') ]),
                       [','])))),
    ]
    
token_patterns = [ ## Patterns applied to tokens.

    Test(lambda tok : tok.iscomment()) % style_token('comment'),

    ]
