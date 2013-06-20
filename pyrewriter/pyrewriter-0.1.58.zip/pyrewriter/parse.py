#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# Python Rewriter parse shortcut code.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import grammar
import token
import predefined


##x Evaluates to root unnamed token that contains top-level tokens produced
##  by applying grammar to text. Grammar can be defined as
##  |pyrewriter.Grammar| instance or as predefined grammar name.
##! Must be used instead of calling |grammar.parseString| since it also
##  adds reference to grammar into tokens that is required for some
##  mechanics to work.
def parse( u_grammar, s_txt ):

  if isinstance( u_grammar, basestring ):
    u_grammar = predefined.predefined( u_grammar )
  ##  Root token.
  oToken = token.Token()
  ##  Grammar definition.
  oGrammar = grammar.Grammar( u_grammar )
  ##  Build expression-name-to-options dictionary.
  oGrammar.analyse()
  for oSubtoken in u_grammar.parseString( s_txt ):
    oToken.addChild( oSubtoken )
  def recursiveSetGrammar( o_token ):
    o_token.grammar = oGrammar
    for oChild in o_token.children():
      recursiveSetGrammar( oChild )
  recursiveSetGrammar( oToken )
  return oToken

