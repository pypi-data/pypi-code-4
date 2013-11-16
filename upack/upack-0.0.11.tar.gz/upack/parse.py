# Copyright (c) 2013, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of upack nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement


import re
import sys

import ply.lex
import ply.yacc

from upack import Package, SubPackage


__all__ = ('parse_manifest',)


reserved = {
    'package': 'PACKAGE',
    'subpackage': 'SUBPACKAGE',
    'exclude': 'EXCLUDE',
}

tokens = (
    'COMMENT',
    'PIPE',
    'PLUS',
    'EQUALS',
    'ATOM',
    'QUOTEDSTRING',
    'TRIQUOTEDSTRING',
    'NOSPACESTRING',
) + tuple(reserved.values())


t_ignore = " \t"

def t_COMMENT(t):
    r'\#.*'
    pass

def t_PIPE(t):
    r'[|]'
    return t

def t_PLUS(t):
    r'[+]'
    return t

def t_EQUALS(t):
    r'='
    return t

def t_ATOM(t):
    r'[a-zA-Z_][-a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ATOM')
    return t

def t_QUOTEDSTRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

def t_TRIQUOTEDSTRING(t):
    r"'''([^\\]|(\\.))*?'''"
    t.value = t.value[3:-3]
    return t

def t_NOSPACESTRING(t):
    r'\S+'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    raise RuntimeError("get me out of here")


def p_manifest(t):
    '''manifest : package subpackages excludes'''
    t[0] = Package(name=t[1].name,
                   options=t[1].options,
                   files=t[1].files,
                   description=t[1].description,
                   subpackages=t[2],
                   excludes=t[3])

def p_empty(t):
    '''empty :
             | COMMENT'''

def p_package(t):
    '''package : PACKAGE ATOM package_options files
               | PACKAGE ATOM package_options files TRIQUOTEDSTRING'''
    name = t[2]
    if 'name' in t[3]:
        name = t[3]['name']
        del t[3]['name']
    if len(t) == 5:
        t[0] = Package(name=name,
                       options=t[3],
                       files=t[4],
                       description=None,
                       subpackages=None,
                       excludes=None)
    elif len(t) == 6:
        t[0] = Package(name=name,
                       options=t[3],
                       files=t[4],
                       description=t[5],
                       subpackages=None,
                       excludes=None)
    else:
        assert False

def p_subpackages(t):
    '''subpackages : empty
                   | subpackage subpackages'''
    if len(t) == 2:
        t[0] = []
    elif len(t) == 3:
        t[0] = [t[1]] + t[2]
    else:
        assert False

def p_subpackage(t):
    '''subpackage : SUBPACKAGE ATOM package_options files
                  | SUBPACKAGE ATOM package_options files TRIQUOTEDSTRING'''
    name = t[2]
    if 'name' in t[3]:
        name = t[3]['name']
        del t[3]['name']
    if len(t) == 5:
        t[0] = SubPackage(name=name, options=t[3], files=t[4],
                          description='<insert description for {name}>')
    elif len(t) == 6:
        t[0] = SubPackage(name=name, options=t[3], files=t[4], description=t[5])
    else:
        assert False

def p_excludes(t):
    '''excludes : empty
              | exclude excludes'''
    if len(t) == 2:
        t[0] = []
    elif len(t) == 3:
        t[0] = [t[1]] + t[2]
    else:
        assert False

def p_exclude(t):
    '''exclude : EXCLUDE NOSPACESTRING'''
    t[0] = t[2]

def p_package_options(t):
    '''package_options : empty
                       | PIPE ATOM EQUALS QUOTEDSTRING package_options
                       | PIPE ATOM ATOM EQUALS QUOTEDSTRING package_options'''
    if len(t) == 2:
        t[0] = {}
    elif len(t) == 6:
        x = t[5].copy()
        if t[2] not in x:
            x[t[2]] = t[4]
        t[0] = x
    elif len(t) == 7:
        x = t[6].copy()
        if t[3] not in x and t[2] in t.parser.tags:
            x[t[3]] = t[5]
        t[0] = x
    else:
        assert False

def p_files(t):
    '''files : empty
             | PLUS NOSPACESTRING files
             | PLUS ATOM NOSPACESTRING files'''
    if len(t) == 2:
        t[0] = []
    elif len(t) == 4:
        t[0] = [t[2]] + t[3]
    elif len(t) == 5:
        if t[2] in t.parser.tags:
            t[0] = [t[2]] + t[3]
        else:
            t[0] = t[3]
    else:
        assert False

def p_error(t):
    if t is not None:
        sys.stderr.write("Syntax error at '%s' on line %d\n" % (t.value, t.lexer.lineno))
    else:
        sys.stderr.write("Syntax error\n")
    raise RuntimeError("get me out of here")


def parse_manifest(infile, tags=None):
    f = open(infile)
    contents = f.read().decode('utf8')
    lexer = ply.lex.lex(reflags=re.UNICODE)
    lexer.lineno = 1
    parser = ply.yacc.yacc(debug=0, write_tables=0)
    parser.tags = tags or set(())
    return parser.parse(contents, lexer=lexer)
