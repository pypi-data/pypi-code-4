#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# |Grammar| class that holds reference to |pyparsing| grammar and some
# additional information about it.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import info


class Grammar( object ):


  def __init__( self, o_root ):
    ##  Reference to actual pyparsing grammar root expression.
    self._root_o = o_root
    self._options_o = {}


  @property
  def options( self ):
    return self._options_o


  @property
  def root( self ):
    return self._root_o


  ##x Will collect options from all grammar expressions.
  def analyse( self ):

    lProcessed = []

    def recursive( o_expr ):
      if o_expr in lProcessed:
        return
      oContext = getattr( o_expr, info.CTX_NAME, None )
      if( oContext ):
        self.options[ oContext[ 'name' ] ] = oContext[ 'options' ]
      lProcessed.append( o_expr )
      if hasattr( o_expr, 'expr' ):
          recursive( o_expr.expr )
      if hasattr( o_expr, 'exprs' ):
        for oExpr in o_expr.exprs:
          recursive( oExpr )

    recursive( self._root_o )

