#!/usr/bin/env python
# coding:utf-8 vi:et:ts=2

# |Token| class that extends |pyparsing| parse results.
# Copyright 2013 Grigory Petrov
# See LICENSE for details.

import info
import parse
import predefined
import re


class ListEx( list ):


  def first( self ):
    return self[ 0 ]


  def last( self ):
    return self[ -1 ]


class Token( object ):


  def __init__(
    self,
    ##i Token name, |None| for root token.
    s_name = None,
    ##i Text, associated with token, |None| for no text.
    s_val = None ):

    self._children_l = []
    self._name_s = s_name
    self.val = s_val
    ##  Contains options passed as strings into |capture|.
    self.options = {}
    ##  Contains reference to |Grammar| instance that has reference to
    ##  grammar used to produce this token and options associated with
    ##  grammar's expressions via |pyrewriter.capture|.
    self.grammar = None
    ##  Reference to parent token, None if this is root token.
    self.parent = None
    ##  Reference to result of last |find...| command.
    self.found = ListEx()


  @property
  def name( self ):
    return self._name_s

  @classmethod
  def selftest( self ):
    oToken = Token()
    assert oToken._quotedStrClosed( "" )
    assert oToken._quotedStrClosed( "a" )
    assert oToken._quotedStrClosed( '""' )
    assert oToken._quotedStrClosed( "''" )
    assert oToken._quotedStrClosed( "''\"\"" )
    assert not oToken._quotedStrClosed( "'" )
    assert not oToken._quotedStrClosed( '"' )
    assert not oToken._quotedStrClosed( "'\"" )
    assert not oToken._quotedStrClosed( "\"'" )
    assert not oToken._quotedStrClosed( "''\"" )
    assert not oToken._quotedStrClosed( "\"\"'" )


  ##@ Modification API.


  ##x Add specified token as sibling before this token.
  ##  Token can be specified following ways:
  ##  * As |Token| object.
  ##  * As |Token.name| string.
  ##  * As |Token.name| and |Token.val| strings.
  ##  * As |s_raw| string that will be parsed via token grammar.
  def addSiblingBefore( self, * args, ** kwargs ):
    kwargs[ 'f_after' ] = False
    return self._addSibling( * args, ** kwargs )


  ##x Add specified token as sibling after this token.
  ##  Token can be specified following ways:
  ##  * As |Token| object.
  ##  * As |Token.name| string.
  ##  * As |Token.name| and |Token.val| strings.
  ##  * As |s_raw| string that will be parsed via token grammar.
  def addSiblingAfter( self, * args, ** kwargs ):
    kwargs[ 'f_after' ] = True
    return self._addSibling( * args, ** kwargs )


  ##x Add specified token as direct child of this token.
  ##  Token can be specified following ways:
  ##  * As |Token| object.
  ##  * As |Token.name| string.
  ##  * As |Token.name| and |Token.val| strings.
  ##  * As |s_raw| string that will be parsed via token grammar.
  def addChild( self, * args, ** kwargs ):
    for oToken in self._tokensFromArgs( * args, ** kwargs ):
      oToken.parent = self
      self._children_l.append( oToken )
    return oToken


  ##x Replace this token with specified token.
  ##  Token can be specified following ways:
  ##  * As |Token| object.
  ##  * As |Token.name| string.
  ##  * As |Token.name| and |Token.val| strings.
  ##  * As |s_raw| string that will be parsed via token grammar.
  ##! If token is specified as raw string and parsing evaluates to more
  ##  that one token, all of them will be added.
  def replace( self, * args, ** kwargs ):
    assert self.parent
    oReplaced = self.addSiblingAfter( * args, ** kwargs )
    self.parent._children_l.remove( self )
    return oReplaced


  ##@ Search API.


  def sibling( self, s_name, s_val = None ):
    lSiblings = self.siblings( s_name, s_val )
    if lSiblings:
      self.found = lSiblings.first()
    else:
      self.found = None
    return self.found


  def siblings( self, s_name, s_val = None ):
    if self.parent:
      return self.parent._descendants( s_name, s_val, f_recursive = False )
    return ListEx()


  def child( self, s_name = None, s_val = None ):
    lChildren = self.children( s_name, s_val )
    if lChildren:
      self.found = lChildren.first()
    else:
      self.found = None
    return self.found


  def children( self, s_name = None, s_val = None ):
    if not s_name:
      return ListEx( self._children_l )
    return self._descendants( s_name, s_val, f_recursive = False )


  def descendant( self, s_name, s_val = None ):
    lDescendants = self.descendants( s_name, s_val )
    if lDescendants:
      self.found = lDescendants.first()
    else:
      self.found = None
    return self.found


  def descendants( self, s_name, s_val = None ):
    return self._descendants( s_name, s_val, f_recursive = True )


  ##x XPath-like search.
  def search( self, s_query ):

    sRe = r'[^\(]*\([^\)]+\)[^\)]*'
    assert re.match( sRe, s_query ), "capture not found in query"

    class Context( object ): pass
    oContext = Context()
    oContext.found = ListEx()

    def recursive( o_token, s_dir, l_rules, o_context ):
      if not l_rules:
        ##  Some path in tokens tree matches entire query.
        return True
      if l_rules[ 0 ] in '/,':
        return recursive( o_token, l_rules[ 0 ], l_rules[ 1: ], o_context )
      else:
        sRule = l_rules[ 0 ]
        if not sRule:
          raise Exception( "direction is not followed by condition" )
        if not s_dir:
          raise Exception( "condition is not preceded by direction" )

        ##  Current token must be captured?
        if sRule.startswith( '(' ) and sRule.endswith( ')' ):
          sRule = sRule[ 1 : -1 ]
          fCapture = True
        else:
          fCapture = False

        ##  Perform search according to current direction.
        sName, _, sVal = sRule.partition( '=' )
        if re.match( r'(\'|\")[^\'\"]*(\'|\")', sVal ):
          sVal = sVal[ 1 : -1 ]
        if '/' == s_dir:
          lTokens = o_token.children( sName, sVal )
        if ',' == s_dir:
          lTokens = o_token.siblings( sName, sVal )

        ##* If |True|, at last one recursive search was successfull.
        fPositiveBranch = False
        ##  Recursively check search results to find paths in tree that
        ##  matches entire query.
        for oToken in lTokens:
          ##  Some path match entire query?
          if recursive( oToken, None, l_rules[ 1 : ], o_context ):
            fPositiveBranch = True
            if fCapture:
              o_context.found.append( oToken )
        return fPositiveBranch

    recursive( self, None, self._splitSearchQuery( s_query ), oContext )
    self.found = oContext.found
    return self.found


  def searchOne( self, s_query ):
    lResult = self.search( s_query )
    if lResult:
      self.found = lResult.first()
    else:
      self.found = None
    return self.found


  ##@ Output API.


  def printit( self, n_indent = 0 ):
    sIndent = ' ' * 2 * n_indent
    print( '{0}{1}({2})'.format( sIndent, self.name, self.val ) )
    for oItem in self._children_l:
      oItem.printit( n_indent + 1 )


  def toStr( self, s_indent = '  ' ):

    class Context( object ): pass

    def recursive( o_token, o_context ):
      ##! Token like '}' unidents itself.
      if 'unindent' in o_token.options:
        assert o_context.indent > 0, "Mismatched umber of { and }"
        o_context.indent -= 1
      if o_token.val:
        ##  Not a first token on the line?
        if o_context.out and not o_context.out.endswith( '\n' ):
          if o_context.lastToken:
            if 'separate' in o_token.options:
              if 'separate' in o_context.lastToken.options:
                  o_context.out += ' '
        ##  First token in the line?
        else:
          o_context.out += o_context.indent * s_indent
        o_context.out += str( o_token.val )
        oContext.lastToken = o_token
      if 'newline' in o_token.options:
        o_context.out += '\n'
      if 'indent' in o_token.options:
        o_context.indent += 1
      for oChild in o_token.children():
        recursive( oChild, o_context )

    oContext = Context()
    oContext.lastToken = None
    oContext.indent = 0
    oContext.out = ""
    recursive( self, oContext )
    return oContext.out


  def __repr__( self ):

    class Context( object ): pass

    def recursive( o_token, o_context ):
      if o_context.out:
        o_context.out += '\n'
      o_context.out += '  ' * o_context.indent
      o_context.out += '{0}( {1} )'.format( o_token.name, o_token.val )
      o_context.indent += 1
      for oChild in o_token.children():
        recursive( oChild, o_context )
      o_context.indent -= 1

    oContext = Context()
    oContext.indent = 0
    oContext.out = ""
    recursive( self, oContext )
    return oContext.out


  ##@ Implementation.


  ##x Used by |addChild|, |addSibling| etc. Creates token from args that
  ##  can be token, one string for name, string and other value for name
  ##  and val, |s_raw| keywoard arg for raw text token representation that
  ##  need to be parsed.
  def _tokensFromArgs( self, * args, ** kwargs ):
    if 's_raw' in kwargs:
      oRoot = parse.parse( self.grammar.root, kwargs[ 's_raw' ] )
      ##! Evaluates to virtual root token.
      return oRoot.children()
    else:
      assert args
      uArg = args[ 0 ]
      if isinstance( uArg, Token ):
        assert 1 == len( args )
        return [ uArg ]
      else:
        assert isinstance( uArg, basestring )
        assert len( args ) in [ 1, 2 ]
        sName = uArg
        sVal = None
        if 2 == len( args ):
          uArg = args[ 1 ]
          assert isinstance( uArg, (basestring, int, long, float) )
          if isinstance( uArg, basestring ):
            sVal = uArg
          else:
            sVal = str( uArg )
        oToken = Token( sName, sVal )
        oToken.grammar = self.grammar
        ##! Get options from grammar definition, if any.
        if sName in oToken.grammar.options:
          oToken.options = oToken.grammar.options[ sName ]
        return [ oToken ]


  def _descendants( self, s_name, s_val = None, f_recursive = True ):

    lFound = []

    def recursive( o_token, l_found ):
      if s_name == o_token.name and (not s_val or s_val == o_token.val):
        l_found.append( o_token )
      if f_recursive:
        for oToken in o_token.children():
          recursive( oToken, l_found )

    for oToken in self.children():
      recursive( oToken, lFound )
    self.found = ListEx( lFound )
    return self.found


  def _addSibling( self, * args, ** kwargs ):
    assert self.parent
    for nChild, oChild in enumerate( self.parent._children_l ):
      if oChild == self:
        lTokens = self._tokensFromArgs( * args, ** kwargs )
        for nToken, oToken in enumerate( lTokens ):
          oToken.parent = self.parent
          nInsertPos = nChild + nToken
          if kwargs.get( 'f_after' ):
            nInsertPos += 1
          self.parent._children_l.insert( nInsertPos, oToken )
        break
    else:
      assert False, "internal consistency error"
    return oToken


  ##x Evaluates to |True| if all single or double quoted strings in
  ##  specified text are closed (or no strings at all).
  def _quotedStrClosed( self, s_txt ):
    sOpenQuote = None
    for i in range( len( s_txt ) ):
      s = s_txt[ i ]
      if s in [ "'", '"' ]:
        ##  This quote starts quoted string?
        if not sOpenQuote:
          sOpenQuote = s
        else:
          ##  This is not verbatim quote?
          if i > 0 and '\\' != s_txt[ i - 1 ]:
            ##  This is same quote that opens string?
            if sOpenQuote == s:
              sOpenQuote = None
    return sOpenQuote is None


  ##x Splits specified text using '/' and ',' delimiter characters while
  ##  allowing them in single or double quoted strings, Evaluates to list of
  ##  parts and delimiters.
  def _splitSearchQuery( self, s_txt ):
    sAccum = ""
    lResult = []
    for s in s_txt:
      if s in '/,' and self._quotedStrClosed( sAccum ):
        if sAccum:
          lResult.append( sAccum )
          sAccum = ""
        lResult.append( s )
      else:
        sAccum += s
    if sAccum:
      lResult.append( sAccum )
    return lResult

if __name__ == '__main__':
  Token.selftest()

