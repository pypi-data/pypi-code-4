#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# Python Rewriter predefined loader code.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import imp
import os


class Context( object ):


  _inst_o = None


  def __init__( self ):
    self.predefined = {}


  @classmethod
  def get( self ):
    if not self._inst_o:
      self._inst_o = Context()
    return self._inst_o


def predefined( s_name ):
  if s_name not in Context.get().predefined:
    sModule = 'predefined_{0}'.format( s_name )
    sFile = '{0}.py'.format( sModule )
    sDir = os.path.dirname( os.path.abspath( __file__ ) )
    sPath = os.path.join( sDir, sFile )
    Context.get().predefined[ s_name ] = imp.load_source( sModule, sPath )
  return Context.get().predefined[ s_name ].GRAMMAR

