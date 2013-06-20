#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# Python Rewriter Library core.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import inspect

from token import Token
from parse import parse
from predefined import predefined
import info


##  List of valid token options that can be passed to |capture|.
ABOUT_OPTIONS = [
  ##  Newline is added after this token, like ';' or '{'.
  'newline',
  ##  Two jointed tokens both haveing this option are separated with space,
  ##  like command and it's arguments.
  'separate',
  ##  This token increase indentation for following tokens, like '{'.
  'indent',
  ##  This token decrease indentation for itself and following tokens,
  ##  like '}'.
  'unindent',
]


def capture( o_expr, * args ):

  mLocals = inspect.currentframe().f_back.f_locals
  for sId in mLocals:
    if id( mLocals[ sId ] ) == id( o_expr ):
      sName = sId
      break
  else:
    assert False, "Object without identifier passed to Capture()"

  mOptions = {}
  for sOption in args:
    assert sOption in ABOUT_OPTIONS
    mOptions[ sOption ] = True

  def parseAction( s_txt, n_pos, o_token ):
    oToken = Token( sName )
    for oChild in [ o for o in o_token if isinstance( o, Token ) ]:
      oToken.addChild( oChild )
    lTxt = [ o for o in o_token if isinstance( o, basestring ) ]
    assert len( lTxt ) < 2
    if lTxt:
      oToken.val = lTxt[ 0 ]
      oToken.options.update( mOptions )
    return oToken
  o_expr.addParseAction( parseAction )

  if not hasattr( o_expr, info.CTX_NAME ):
    setattr( o_expr, info.CTX_NAME, { 'name': sName, 'options': mOptions } )
  else:
    assert False, "Single object captured more than once"

