#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- file: ccodeinline.py -*-

### 
### Copyright (c) 2009-2013 << Patrick. Riendeau, Maxiste Deams >>.
### All rights reserved.
### 
### Redistribution and use in source and binary forms are permitted
### provided that the above copyright notice and this paragraph are
### duplicated in all such forms and that any documentation,
### advertising materials, and other materials related to such
### distribution and use acknowledge that the software was developed
### by the UnderscoreX.  The name of the
### UnderscoreX may not be used to endorse or promote products derived
### from this software without specific prior written permission.
### THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
### IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
### WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
###



import os, sys, re 
import numpy as np
import multiprocessing 
import imp
import tempfile 
from tempfile import NamedTemporaryFile

### Taked out of _build_install_module 
from distutils.core import setup, Extension

###############################################################################
# Compilation lock for multiprocessing.                                       #
###############################################################################
_COMP_LOCK = multiprocessing.Lock()

###############################################################################
# Module setup.                                                               #
###############################################################################

class CCITypeSupportWarning( Warning ):
  msg                             = 'Warning This type is not supported by the current processor. Value:{}'
  def __init__( self, value ):
    Warning.__init__( self, self.msg.format( value ) )


class CCITypeDictWarning( Warning ):
  msg                             = 'Warning will not accept this Dict-Type inside this property: Dict:{}'
  def __init__( self, value ):
    Warning.__init__( self, self.msg.format( value ) )

class CCItagRegistrationWarning( Warning ):
  msg                             = 'Warning Tag is not registred inside ListTag, TAG:{}'
  def __init__( self, value ):
    Warning.__init__( self, self.msg.format( value ) )

class CCITagDictWarning( Warning ):
  msg                             = 'Warning Tag is not listed inside Operation-Dict and will not be parsed, TAG:{}'

  def __init__( self, value ):
    Warning.__init__( self, self.msg.format( value ) )

class CCITagSkeletonWarning( Warning ):
  msg                             = 'Warning Tag is not found inside Skeleton and will not be located.'

  def __init__( self, value ):
    Warning.__init__( self, self.msg.format( value ) )

class CCIIncludeTypeDictException( Exception ):
  msg                             = 'Exception, use of property self.IncludeHeaderType is mandatory prior to call property '

  def __init__( self, value ):
    Warning.__init__( self, self.msg.format( value ) )
  

class CCodeInline( object ):

  _SKEL = r'''

  __INCLUDE_HEADER__
  
  // Forward declarations of our function.
  static PyObject *__FUNCTION__(PyObject *self, PyObject *args); 


  // Boilerplate: function list.
  static PyMethodDef methods[] = {
      { "__FUNCTION__", __FUNCTION__, METH_VARARGS, "Doc string."},
      { NULL, NULL, 0, NULL } /* Sentinel */
  };

  // Boilerplate: Module initialization.
  PyMODINIT_FUNC init__MODULE_NAME__(void) {
          (void) Py_InitModule("__MODULE_NAME__", methods);
          import_array();
  }


  /*****************************************************************************
   * Array access macros.                                                      *
   *****************************************************************************/
  __NUMPY_ARRAY_MACROS__


  /*****************************************************************************
   * Support code.                                                             *
   *****************************************************************************/
  __SUPPORT_CODE__


  /*****************************************************************************
   * The function.                                                             *
   *****************************************************************************/
  PyObject *__FUNCTION__(PyObject *self, PyObject *args) {


  /***************************************
   * Variable declarations.              *
   ***************************************/
  __FUNC_VAR_DECLARATIONS__


  /***************************************
   * Parse variables.                    *
   ***************************************/
  if (!PyArg_ParseTuple(args, "__PARSE_ARG_TYPES__", __PARSE_ARG_LIST__))
  {
      return NULL;
  } 


  /***************************************
   * User code.                          *
   ***************************************/
  __USER_CODE__


  /***************************************
   * Return value.                       *
   ***************************************/
  __RETURN_VAL__

  } // End of function(self, args).

  '''
  IncludeType={ 'internal':[ 'Python.h', 'numpy/arrayobject.h', 'math.h' ],
                'external':[ ],
                'key-list':[ 'internal','external' ] }

  ListTag=[ '__INCLUDE_HEADER__', '__FUNCTION__','__MODULE_NAME__','__NUMPY_ARRAY_MACROS__','__SUPPORT_CODE__',
            '__FUNC_VAR_DECLARATIONS__','__PARSE_ARG_TYPES__','__PARSE_ARG_LIST__','__USER_CODE__','__RETURN_VAL__' ]

  ListTypeDict=( '_TYPE_CONV_DICT', '_RETURN_FUNC_DICT', '_TYPE_PARSE_SPEC_DICT' , '_NP_TYPE_CONV_DICT' )

  __Loader__=[ 'SetNpFloat128','SetTempDirCompilation','SetSystemTypeLib' ]

  DictOperation={ '__MODULE_NAME__':'_gen_name',
                  '__FUNCTION__':'_gen_function',
                  '__INCLUDE_HEADER__':'_gen_include_header',
                  '__SUPPORT_CODE__':'_gen_support_code',
                  '__USER_CODE__':'_gen_code',
                  '__NUMPY_ARRAY_MACROS__':'_gen_numpy_array_macros',
                  '__FUNC_VAR_DECLARATIONS__':'_gen_var_decls',
                  '__PARSE_ARG_TYPES__':'_gen_parse_arg_types',
                  '__PARSE_ARG_LIST__':'_gen_parse_arg_list',
                  '__RETURN_VAL__':'_gen_return_val' } 

  ### Warning Thresold, way to disable some, but not all of Warning...
  ### Due to presence of Tag-Property, While you add this tag inside the
  ### property mechanism, you may print out this property and will tell True/False
  ### the presence of this tag Inside the Skeleton... While it may be usefull to
  ### bypass a warning level to automation purposes. 
  IsDisabledCCITagSkeletonWarning = True 

  ### 
  ### Property to manage _SKEL
  ### Possibility to manage more than one skeleton and will imply to set a current Skeleton,
  ### to set a variable receiving the copy of the skeleton and obviously a variable that will
  ### name the Skeleton to be reflected thru a property that query the current skeleton set
  ### and display actual modification. We also understand at this point it should save the
  ### actual skeleton and switch to another.
  ### 

  # This is a dictionary mapping unique names to their functions. 
  _FUNCS = {}


  Platform                = { 'lib':{ 'widows':'{}.dll',
                                      'linux':'{}.so',
                                      'osx':'{}.so' } }
  SkeletonDict            = { 0:{ 'Body':None, 'Include':[] , 'function_name':'function' }  }
  SkeletonTagVar          = None 
  SkeletonIndexVar        = 0
  SkeletonSubIndexVar     = 'Body'
  ModSkeletonVar          = None
  SubIndexSkelFormatVar   = None
  RegExpTagDetection      = r'(?mui){}'
  RegExpHeaderDetection   = r'(?ui)[<\'\"]{}[>\'\"]'
  _PATH                   = '/tmp/np_inline' 
  TemporaryFile           = None
  IndexTypeDictVar        = None
  TypeDictVar             = None
  IncludeHeaderTypeVar    = None
  IncludeHeaderVar        = None
  IncludeHeaderParsedVar  = None 
  ContextOSVar            = None
  OSLibVar                = None
  OSLibFormatVar          = None
  ContextLibOsVar         = None 
  
  ### Before : np_type
  NpTypeVar               = None

  ### Before : dims
  DimsVar                 = None

  ### Before : c_name 
  CNameVar                = None

  ### Before : c_code
  CCodeVar                = None 

  ### Before : mod_name
  ModNameVar              = None 

  ### keeped Untouched 

  ### From original doc.
  ### args : tuple
  ###        The arguments passed to the C function. Currently the code can
  ###        accept python ints and floats, as well as numpy numeric arrays 
  ###        of all types. Numpy objects should always be after other 
  ###        objects, and types should correspond with the definitions given
  ###        in py_types and np_types respectively. 
  args=()

  ### From original doc.
  ###  py_types : tuple of tuples (python_type, c_name)
  ###             Type specifications for non-numpy arguments. Currently only int 
  ###             and float are valid types. Default is empty tuple.
  py_types=()

  ### From original doc.
  ###  np_types : tuple of tuples (numpy_type, dims, c_name) : Now ( FNpType, FDims, FCName )
  ###             Type specifications for numpy-type arguments. Most numeric numpy 
  ###             types are valid. FDims is the integer number of dimensions of the 
  ###             corresponding array. Default is empty tuple.
  np_types=()

  ### From original doc.
  ###  code : string, optional 
  ###         C-code. One of code and code_path must be given.
  ### code=None
  ### Was replaced by a Property -> FCCode
  

  ### From original doc.
  ### code_path : string, optional
  ###             Full path to c-code. One of code or code_path should be given.
  code_path=None

  ### From original doc.
  ### support_code : string, optional 
  ###                C support code. This code will be inserted before the function 
  ###                containing the c-code above. This can include any valid C code 
  ###                including #includes and #defines.  
  support_code=None

  ### From original doc.
  ### support_code_path : string, optional
  ###      Full path to support code.
  support_code_path=None
  
  ### From original doc.
  ###   extension_kwargs : dictionary, optional
  ###                      Keyword arguments to pass to the distutils.Extension constructor.
  extension_kwargs={}

  ### From original doc.
  ###  return_type : python primitive type
  ###                Either int or float.  
  return_type=None

  ### From original doc.
  ###    unique_name : string
  ###                  A unique string identifying this bit of code. This should be valid
  ###                  to use as a filename.
  UniqueNameVar = None 

  ### Property-platform to manage property of platform specific need.
  def GetContextOS( self ):
    return self.Platform[ self.ContextOSVar ] 

  def SetContextOS( self, value ):
    self.ContextOSVar = value

  ContextOS=property( GetContextOS, SetContextOS )

  @property
  def ContextOSList( self ):
    return getattr( self.ContextOS, 'keys')()

  @property
  def ContextLibOs( self ):
    ### This method was improved to do a first-check and initialize
    ### the self.ContextLibOsVar to Os-type specific library format
    ### and even if the code work on second call on this variable
    ### self.ContextLibOsVar, it will be surprizing to found this
    ### instance changing from OS instantly. This is why it does
    ### the verification only once. 
    ReturnValue=None
    ReturnIndex=None
    if self.ContextLibOsVar != None:
      ReturnValue=self.ContextLibOsVar
    else:
      StrPlatform = sys.platform
      for ItemStrReg in self.ContextOSList:
        Areg=re.compile( r'(?ui){}'.format( ItemStrReg ) )
        if Areg.match( StrPlatform ):
          ReturnIndex = ItemStrReg
      self.ContextLibOsVar = self.ContextOS[ ReturnIndex ]
      ReturnValue = self.ContextLibOsVar
    return ReturnValue
   
  
  ### Property SkeletonIndex, will define the current Index, ready to look inside a SkeletonDict[ X ]
  def GetIndexSkel( self ):
    return self.SkeletonIndexVar

  def SetIndexSkel( self , value ):
    self.SkeletonIndexVar = value

  SkeletonIndex = property( GetIndexSkel, SetIndexSkel )

  def GetSubIndexSkelFormat( self ):
    return self.SubIndexSkelFormatVar

  def SetSubIndexSkelFormat( self, value ):
    self.SubIndexSkelFormatVar = value 

  ### this property will define what is the next type to be use to create a SubIndex In a Current SkeletonDict[ n ][ ? ]
  SubIndexSkelFormat = property(GetSubIndexSkelFormat, SetSubIndexSkelFormat)

  ### this property will add the SubIndex to SkeletonDict[ n ][ Y ] and it's format for variable being inserted here. 
  @property
  def AddSubIndexSkel( self ):
    if self.SubIndexSkel not in self.SkeletonDict.keys():
      if self.SubIndexSkelFormat == None:
        self.SkeletonDict[ self.SkeletonIndex ][ self.SubIndexSkel ]=None
      else:
        self.SkeletonDict[ self.SkeletonIndex ][ self.SubIndexSkel ]=getattr( __builtins__, self.SubIndexSkelFormat )()

  def GetSubIndexSkel( self ):
    return self.SkeletonSubIndexVar

  def SetSubIndexSkel( self , value ):
    self.SkeletonSubIndexVar = value 

  ### This property define only the current Index in a Current SkeletonDict[ ? ]
  SubIndexSkel = property( GetSubIndexSkel, SetSubIndexSkel ) 

  ### This property will add inside current SkeletonDict[ X ], a fresh copy of self._SKEL.
  ### Re-using it during an operation inside function listed inside self.DictOperation will
  ### dump a clean copy leaving all modification to disappear. 
  @property
  def AddSkeleton( self ):
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'Body'
    self.SkeletonDict[ self.SkeletonIndex ]={ self.SubIndexSkel:str( self._SKEL ),
                                              'Include':[ ],
                                              'function_name':'function' }
    self.SubIndexSkel=OldIndex
  
  ### Property VarDefSkeleton, will give us the content of SkeletonDict[ X ], and will acces to it to
  ### change anything... Not really used or it will overwrite everything 
  def GetVSkeleton( self ):
    ValueReturn=False
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'Body'
    ValueReturn = self.SkeletonDict[ self.SkeletonIndex ][ self.SubIndexSkel ]
    self.SubIndexSkel=OldIndex
    return ValueReturn
    

  def SetVSkeleton( self , value ):
    ### Note: Its important to save the current self.SubIndexSkel, being used anywhere
    ### at any moment, an example like a parse of header-include is using self.SubIndexSkel = 'Include'
    ### you will store to a wrong place the value here... restoring it after will allow the parser to
    ### continue... 
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'Body'
    self.SkeletonDict[ self.SkeletonIndex ][ self.SubIndexSkel ] = value
    self.SubIndexSkel=OldIndex

  VarDefSkeleton = property( GetVSkeleton ,  SetVSkeleton )

  ### Property VarDefFunction, will give us the content of SkeletonDict[ X ][ 'function_name' ], and will acces to it to
  ### change anything... Not really used or it will overwrite everything 
  def GetVFunc( self ):
    ValueReturn=False
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'function_name'
    ValueReturn = self.SkeletonDict[ self.SkeletonIndex ][self.SubIndexSkel]
    self.SubIndexSkel=OldIndex
    return ValueReturn
    

  def SetVFunc( self , value ):
    ### Note: Its important to save the current self.SubIndexSkel, being used anywhere
    ### at any moment, an example like a parse of header-include is using self.SubIndexSkel = 'Include'
    ### you will store to a wrong place the value here... restoring it after will allow the parser to
    ### continue... 
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'function_name'
    self.SkeletonDict[ self.SkeletonIndex ][ self.SubIndexSkel ] = value 
    self.SubIndexSkel=OldIndex

  VarDefFunction = property( GetVFunc ,  SetVFunc )

  ### Property to manage Include Header between IncludeType and SkeletonDict. This may lead to
  ### affect the Skeleton Body by presuming we storing change and Include header altogether
  ### In case we change our mind and add #if-#elif-#endif clause and need to surround an
  ### include from this possibility... Or simple remove header or having floating header
  ### becoming permanent inside a distribution... unlike 'Python.h' was set like this in many
  ### Bsd / FreeBSD and become <Python.h>  around 1997 where Python start to be much stronger.

  def GetIncHeaderType( self ):
    return self.IncludeHeaderTypeVar

  def SetIncHeaderType( self, value ):
    self.IncludeHeaderTypeVar = value

  ### A property to configure which type of Header we are expecting to analyse
  ### 2-choice, internal, external 
  IncludeHeaderType = property( GetIncHeaderType, SetIncHeaderType )

  def GetIncludeHFormat( self ):
    ValueReturn=False
    StrRegExp=str( self.RegExpHeaderDetection )
    Areg=re.compile( StrRegExp.format( self.IncludeHeaderVar ) )
    if len( Areg.findall( str( self.VarDefIncludeHeader ) )  ) > 0 :
      ValueReturn=True
    return ValueReturn 

  def SetIncludeHFormat( self, value ):
    self.IncludeHeaderVar = value

  ### Assuming we had self.IncludeHeaderVar holding an Include-Header
  ### it will return true/false if this one is parsed and inserted inside
  ### SkeletonDict[ n ][ Include ]
  IncludeHeaderFormat = property( GetIncludeHFormat, SetIncludeHFormat )

  def GetIncHeader( self ):
    ValueReturn = None 
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'Include'
    ValueReturn = self.SkeletonDict[ self.SkeletonIndex ][self.SubIndexSkel]
    self.SubIndexSkel=OldIndex
    return ValueReturn
    

  def SetIncHeader( self , value ):
    ### Note: Its important to save the current self.SubIndexSkel, being used anywhere
    ### at any moment, an example like a parse of header-include is using self.SubIndexSkel = 'Include'
    ### you will store to a wrong place the value here... restoring it after will allow the parser to
    ### continue... 
    OldIndex=self.SubIndexSkel
    self.SubIndexSkel = 'Include'
    self.SkeletonDict[ self.SkeletonIndex ][ self.SubIndexSkel ].append( value )
    self.SubIndexSkel=OldIndex

  ### property that extract all header from SkeletonDict[ n ][ Include ] if this
  ### property is called alone.
  ### This property called with affectation, will add another include-header inside the list
  ### of SkeletonDict[ n ][ Include ].
  ### So it have to be parsed and formed as internal like Header : '<Header.h>' or
  ### external : 'Header.h' 
  VarDefIncludeHeader = property( GetIncHeader ,  SetIncHeader )  

  def GetIncludeHeader( self ):
    return self.IncludeHeaderParsedVar

  def SetIncludeHeader( self, value ):
    ValueSet=None 
    if self.IncludeHeaderType == 'internal':
      ValueSet = '<{}>'.format( value )
    if self.IncludeHeaderType == 'external':
      ValueSet = '\'{}\''.format( value )
    self.IncludeHeaderParsedVar = ValueSet

  ### These one depend of property IncludeHeaderType, but define
  ### how a future Include header will appear inside the SkeletonDict[ n ][ Include ].
  ### as <Header.h> or 'Header.h' format... 
  ParseIncludeHeader = property( GetIncludeHeader, SetIncludeHeader ) 

  def GetToDictIncludeHeader( self ):
    return self.IncludeType[ self.IncludeHeaderType ]

  def SetToDictIncludeHeader( self , value ):
    if self.IncludeHeaderType not in self.IncludeType['key-list']:
      raise CCIIncludeTypeDictException, 'IncludeHeaderType not set properly.'
    else:
      self.IncludeType[ self.IncludeHeaderType ].append( value )

  DictIncludeHeader = property( GetToDictIncludeHeader, SetToDictIncludeHeader )

  @property
  def UpdateIncludeHeader( self ):
    for StrKeyIncludeH in self.IncludeType['key-list']:
      ### Defining If by Turn, internal / external
      ### type from self.IncludeType keys....
      self.IncludeHeaderType = StrKeyIncludeH
      ### this mean we can directly get an Include Header from self.IncludeType[<internal | external>]
      ### and use self.ParseIncludeHeader to directly get a parsed header, ready to add inside self.VarDefIncludeHeader
      ### which directly forward all parsed-item inside SkeletonDict[ n ][ Include ].
      for StrHeader in self.DictIncludeHeader :
        ### Will result a parsed-header here.
        if StrHeader is not None:
          self.ParseIncludeHeader = StrHeader
        ### This property test if an header is present inside SkeletonDict[ n ][ Include ].
        ### We will not re-insert many identical header...
        if self.ParseIncludeHeader is not None :
          self.IncludeHeaderFormat =  self.ParseIncludeHeader
        if self.IncludeHeaderFormat == False:
          ### Will be added inside SkeletonDict[ n ][ Include ]
          self.VarDefIncludeHeader = self.ParseIncludeHeader


  ### Property SkeletonChange, will change it and give us the result. need to add another Property, The Tag
  ### Property to allow sibling a TAG inside a Skeleton and replace-it . Using the property IsSkeletonTag
  ### will add a value with current TAG, printing the IsSkeletonTag, will tell you true/false if tag can be
  ### found.

  def GetSkeletonTag( self ):
    IsSearch=re.compile( self.RegExpTagDetection.format( self.SkeletonTagVar ) )
    valueReturn = False
    if len( IsSearch.findall( self.VarDefSkeleton )) > 0:
      valueReturn = True
    if self.IsDisabledCCITagSkeletonWarning and valueReturn == False:
      raise CCITagSkeletonWarning, self.SkeletonTagVar
    return valueReturn

  def SetSkeletonTag( self, value ):
    if value not in self.ListTag :
      raise CCItagRegistrationWarning, value
    if value not in self.DictOperation.keys() :
      raise CCITagDictWarning, value 
      
    self.SkeletonTagVar = value

  @property
  def CurrentSkeletonTag( self ):
    return self.SkeletonTagVar
    
  IsSkeletonTag = property( GetSkeletonTag, SetSkeletonTag )

  ### After feeding SkeletonIndex + IsSkeletonTag
  ### Internal property SetModSkeleton of SkeletonChange will change the tag
  ### by the value, and remaining getter from this property will output change .
  def GetModSkeleton( self ):
    return self.ModSkeletonVar

  def SetModSkeleton( self , value ):
    if value == None:
      value=str()
    StrSkelChg = str( self.VarDefSkeleton )
    self.ModSkeletonVar = StrSkelChg.replace( self.CurrentSkeletonTag, value )  
    
  SkeletonChange = property( GetModSkeleton, SetModSkeleton )

  ### This property dump last modification inside the location SkeletonDict[ X ]
  @property
  def UpdateSkeleton( self ):
    self.VarDefSkeleton = self.SkeletonChange

  ### Finally This property will update the Current Skeleton, into it's SkeletonDict[ X ] location.
  ### Assuming we can do error here, we only need to ask to create a new SkeletonDict[ Y ] or
  ### calling back self.AddSkeleton 

  ### 
  ### End of Property to manage _SKEL
  ### And Halloween is not yet here... In a couple of days.  
  ### 

  

  ###
  ### Property to manage Dict _TYPE_CONV_DICT, _RETURN_FUNC_DICT, _TYPE_PARSE_SPEC_DICT. 
  ###
  ### Theses method shall manage and extract the content of all dict _TYPE_CONV_DICT, _RETURN_FUNC_DICT, _TYPE_PARSE_SPEC_DICT. 
  ### using One by one, TypeDict + IndexTypeDict you configure the property Variable to be ready to use QueryValueTypeDict
  ### to extract current CurrentDict[ CurrentIndex ]... Using AddValueTypeDict after having configured properly TypeDict + IndexTypeDict
  ### will add instantly a value in form CurrentDict[ CurrentIndex ]=value, overwriting value should not be usefull since 
  ### default model offer inside np_inline is good and should not <<opting>> for a better idiom. 
  ###
  
  def GetTypeDict( self ):
    return self.TypeDictVar

  def SetTypeDict( self, value ):
    if value not in self.ListTypeDict:
      raise CCITypeDictWarning, value

    if value in self.ListTypeDict:
      self.TypeDictVar = value

  TypeDict=property( GetTypeDict, SetTypeDict )

  def GetIndexTypeDict( self ):
    return self.IndexTypeDictVar

  def SetIndexTypeDict( self , value ):
    self.IndexTypeDictVar = value

  IndexTypeDict = property( GetIndexTypeDict, SetIndexTypeDict )

  @property 
  def QueryValueTypeDict( self ):
    TypeDict=getattr( self, self.TypeDict )
    return TypeDict[ self.IndexTypeDict ]


  def GetValueTypeDict( self ):
    return getattr( self, self.TypeDict)[ self.IndexTypeDict ]
  
  def SetValueTypeDict( self, value ):
    getattr( self, self.TypeDict)[ self.IndexTypeDict ]=value

  AddValueTypeDict=property( GetValueTypeDict, SetValueTypeDict ) 
    
  ###
  ### End of property for managing Dict _TYPE_CONV_DICT, _RETURN_FUNC_DICT, _TYPE_PARSE_SPEC_DICT. 
  ###


  ### 
  ### Property to manage Function. 
  ###

  def GetNpType( self ):
    return self.NpTypeVar 

  def SetNpType( self, value  ):
    self.NpTypeVar =  value

  FNpType = property( GetNpType, SetNpType )

  def GetDims( self ):
    return self.DimsVar 

  def SetDims( self, value  ):
    self.DimsVar =  value

  FDims = property( GetDims, SetDims )

  ### Removed property FCName, FUniqueName was resolved and found in transfert between
  ### inline and _gen_code which was the first parameter. 
  def GetCName( self ):
    return self.CNameVar 

  def SetCName( self, value  ):
    self.CNameVar =  value

  FCName = property( GetCName, SetCName )

  def GetCCodeVar( self ):
    return self.CCodeVar

  def SetCCodeVar( self, value ):
    self.CCodeVar = value

  ### Is replacing c_code and code
  ### Shoold end into __USER_CODE__
  ### And inside _build_install_module we should read actual
  ### code from skeleton... 
  FCCode = property( GetCCodeVar, SetCCodeVar )

  def GetModNameVar( self ):
    return self.ModNameVar

  def SetModNameVar( self, value ):
    self.ModNameVar = value

  ### Is replacing mod_name 
  FModName = property( GetModNameVar, SetModNameVar )

  def GetUniqueName( self ):
    return self.UniqueNameVar

  def SetUniqueName( self, value ):
    self.UniqueNameVar = value

  ### Is Replacing unique_name
  FUniqueName = property( GetUniqueName, SetUniqueName )
   

#  def Get( self ):
#    return self.
#
#  def Set( self, value ):
#    self. = value
#
#  F = property( Get, Set )

  
  ### 
  ### End of property to mange Function 
  ### 
  _TYPE_CONV_DICT = {
      float : 'double',
      int   : 'long',
      str   : 'str'
  }


  _RETURN_FUNC_DICT = {
    float : 'PyFloat_FromDouble',
    int   : 'PyLong_FromLong',
    str   : 'PyString_FromString'
  }


  _TYPE_PARSE_SPEC_DICT = {
    float : 'd',
    int   : 'i',
    str   : 's'
  }

  _NP_TYPE_CONV_DICT = {
      np.uint8    : 'npy_uint8',
      np.uint16   : 'npy_uint16',
      np.uint32   : 'npy_uint32',
      np.uint64   : 'npy_uint64',
      np.int8     : 'npy_int8',
      np.int16    : 'npy_int16',
      np.int32    : 'npy_int32',
      np.int64    : 'npy_int64',
      np.float32  : 'npy_float32',
      np.float64  : 'npy_float64',
  }

  ### Keep-it it's Dict-Reference for PyBuild_value
  _TYPE_PARSE_PY_BUILD = {
    's':{ 'py_type':str,
          'c_type':'char *' }, 
    's#':{ 'py_type':str,
           'c_type':'char *' }, 
    'z':{ 'py_type':str,
          'c_type':'char *' }, 
    'z#':{ 'py_type':str,
           'c_type':'char *' }, 
    'u':{ 'py_type':unicode,
          'c_type':'Py_UNICODE *' }, 
    'u#':{ 'py_type':unicode,
           'c_type':'Py_UNICODE *' }, 
    'i':{ 'py_type':int,
          'c_type':'int' }, 
    'b':{ 'py_type':int,
          'c_type':'char' }, 
    'h':{ 'py_type':int,
          'c_type':'short int' }, 
    'l':{ 'py_type':int,
          'c_type':'long int' }, 
    'B':{ 'py_type':int,
          'c_type':'unsigned char' }, 
    'H':{ 'py_type':int,
          'c_type':'unsigned short int' }, 
    'I':{ 'py_type':int,
          'c_type':'unsigned int' }, 
    'k':{ 'py_type':int,
          'c_type':'unsigned long' }, 
    'L':{ 'py_type':long,
          'c_type':'PY_LONG_LONG' }, 
    'K':{ 'py_type':long,
          'c_type':'unsigned PY_LONG_LONG' }, 
    'n':{ 'py_type':int,
          'c_type':'Py_ssize_t' }, 
    'c':{ 'py_type':str,
          'c_type':'char' }, 
    'd':{ 'py_type':float,
          'c_type':'double' }, 
    'f':{ 'py_type':float,
          'c_type':'float' }, 
    'D':{ 'py_type':complex,
          'c_type':'Py_complex *' }, 
    'O':{ 'py_type':object,
          'c_type':'PyObject *' }, 
    'S':{ 'py_type':object,
          'c_type':'PyObject *' }, 
    'N':{ 'py_type':object,
          'c_type':'PyObject *' }, 
    'O&':{ 'py_type':object,
           'c_type':'Any' }, 
    '(items)':{ 'py_type':None,
                'c_type':None }, 
    '[items]':{ 'py_type':None,
                'c_type':None }, 
    '{items}':{ 'py_type':dict,
                'c_type':None }, 
  }



  def GenerateCode( self ):
    for ItemIndex in self.DictOperation.keys():
      self.IsSkeletonTag = ItemIndex
      getattr( self, self.DictOperation[ ItemIndex ] )( ) 
      self.UpdateSkeleton

  def _gen_name( self ):
    self.SkeletonChange = self.FUniqueName

  def _gen_function( self ):
    self.SkeletonChange = self.VarDefFunction

  def _gen_include_header( self ):
    self.UpdateIncludeHeader
    StrHeaderAdd='\n'
    for Item in self.VarDefIncludeHeader:
      StrHeaderAdd += "{}\n".format( Item )
    self.SkeletonChange = StrHeaderAdd

  def _gen_support_code( self ):
    self.SkeletonChange = self._string_or_path( self.support_code, self.support_code_path )

  def _gen_code( self ):
    self.SkeletonChange = self._string_or_path( self.FCCode, self.code_path )

      
  ### Part of DictOperation pattern substitution. 
  def _gen_var_decls( self ):
    StrTagValue = str()
    ### py_types moved to self.
    ### np_types moved to self.
    ### return_type moved to self.
    ### Internal-var being pushed inside property .
    ### Following variable  where involved inside argument declaration of
    ### def. 
    # self.FNpType, ------ replace --> np_type
    #    self.FDims, ----- replace --> dims
    #       self.FCName -- replace --> c_name
    """py_types should be a list with elements of the form
    (python_object, python_type, self.FCCodeVar_name)
    
    np_types should be a list with elements of the form 
    (numpy_object, numpy_type, num_dims, self.FCCodeVar_name)
    """
    str_list = []
    self.TypeDict = '_TYPE_CONV_DICT'
    for py_type, self.FCName in self.py_types:
      ### Moving uses of [ --> c_type = _TYPE_CONV_DICT[py_type] <-- ] into
      ### use of self.TypeDict + self.IndexTypeDict 
      #c_type = _TYPE_CONV_DICT[py_type]
      self.IndexTypeDict=py_type
      str_list.append('{0} {1};'.format(self.QueryValueTypeDict, self.FCName))

    for self.FNpType, self.FDims, self.FCName in self.np_types:
      str_list.append('PyArrayObject *py_{0};'.format(self.FCName))

    self.TypeDict = '_TYPE_CONV_DICT'
    if self.return_type is not None:
      ### Moving uses of [ --> c_type = _TYPE_CONV_DICT[py_type] <-- ] into
      ### use of self.TypeDict + self.IndexTypeDict 
      #c_type = _TYPE_CONV_DICT[self.return_type]
      self.IndexTypeDict=self.return_type
      str_list.append('{0} return_val;'.format(self.QueryValueTypeDict))

    self.SkeletonChange = '\n'.join(str_list)

  ### Part of DictOperation pattern substitution. 
  def _gen_parse_arg_types( self ):
    StrTagValue = str()
    ### py_types moved to self.
    ### np_types moved to self.
    ### Following variable  where involved inside argument declaration of
    ### def. 
    # self.FNpType, ------ replace --> np_type
    #    self.FDims, ----- replace --> dims
    #       self.FCName -- replace --> c_name
    str_list = []
    self.TypeDict = '_TYPE_PARSE_SPEC_DICT'
    for py_type, self.FCName in self.py_types:
      self.IndexTypeDict=py_type      
      ### Moving uses of [ --> str_list.append(_TYPE_PARSE_SPEC_DICT[py_type]) <-- ] into
      ### use of self.TypeDict + self.IndexTypeDict 
      #str_list.append(_TYPE_PARSE_SPEC_DICT[py_type])
      str_list.append( self.QueryValueTypeDict ) 

    for self.FNpType, self.FDims, self.FCName in self.np_types:
      str_list.append('O')
        
    self.SkeletonChange = ''.join(str_list)

  ### Part of DictOperation pattern substitution. 
  def _gen_parse_arg_list(self):
    StrTagValue = str()
    ### py_types moved to self.
    ### np_types moved to self.
    ### Following variable  where involved inside argument declaration of
    ### def. 
    # self.FNpType, ------ replace --> np_type
    #    self.FDims, ----- replace --> dims
    #       self.FCName -- replace --> c_name
    str_list = []

    for py_type, self.FCName in self.py_types:
      str_list.append('&{0}'.format( self.FCName ))

    for self.FNpType, self.FDims, self.FCName in self.np_types:
      str_list.append('&py_{0}'.format( self.FCName ))
        
    self.SkeletonChange = ', '.join(str_list)

  ### Part of DictOperation pattern substitution. 
  def _gen_numpy_array_macros( self ):
    ### np_types moved to self.np_types
    ### Following variable  where involved inside argument declaration of
    ### def. 
    # self.FNpType, ------ replace --> np_type
    #    self.FDims, ----- replace --> dims
    #       self.FCName -- replace --> c_name
    StrTagValue = str()
    str_list = []
    for self.FNpType, self.FDims, self.FCName in self.np_types:
      #, self.FDims, self.FCName = np_type, self.FDims, self.FCName
      str_list.append( _gen_numpy_array_index_macro( ) )
      s = '#define {0}_shape(i) (py_{0}->dimensions[(i)])'.format( self.FCName )
      str_list.append(s)
      s = '#define {0}_ndim (py_arr->nd)'.format( self.FCName )
      str_list.append(s)
    self.SkeletonChange = '\n'.join(str_list)

  ### Part of sub-function of _gen_numpy_array_macros
  def _gen_numpy_array_index_macro( self ):
    StrTagValue = str()
    ### np_type moved to self.np_type
    ### dims moved to self.dims
    ### c_name moved to self.c_name
    ### Moving uses of _NP_TYPE_CONV_DICT[self.np_type] into
    ### use of self.TypeDict + self.IndexTypeDict 
    ### Following variable  where involved inside argument declaration of
    ### def. 
    # self.FNpType, ------ replace --> np_type
    #    self.FDims, ----- replace --> dims
    #       self.FCName -- replace --> c_name
    self.TypeDict = '_NP_TYPE_CONV_DICT'
    self.IndexTypeDict = self.FNpType 
    #c_type = self.QueryValueTypeDict
    #c_type = self._NP_TYPE_CONV_DICT[self.np_type]

    # First we generate the list of arguments for the macro. 
    # These have the form x0, x1, ...
    arg_list = ', '.join( ['x{0}'.format(i) for i in range( self.FDims )] )

    # Next, we want to create the indexing code. This looks like:
    # *(type *)((data + i*array->strides[0] + j*array->strides[1]))
    strides = ''
    for i in range( self.FDims ):
      strides += ' + (x{0}) * py_{1}->strides[{0}]'.format( i, self.FCName )
    
    return '#define {0}({1}) *({2} *)((py_{0}->data {3}))'.format( self.FCName ,
                                                                   arg_list,
                                                                   self.QueryValueTypeDict,
                                                                   strides )


  ### Part of DictOperation pattern substitution. 
  def _gen_return_val( self ):
    ### return_type moved to self.return_type
    ### Following variable  where involved inside argument declaration of
    ### def. 
    # self.FNpType, ------ replace --> np_type
    #    self.FDims, ----- replace --> dims
    #       self.FCName -- replace --> c_name
    StrTagValue = str()
    if self.return_type is None:
      StrTagValue = 'Py_RETURN_NONE;'
    else:
      self.TypeDict = '_RETURN_FUNC_DICT'
      self.IndexTypeDict=self.return_type
      StrTagValue ='return {0}(return_val);'.format( self.QueryValueTypeDict )
      
    self.SkeletonChange = StrTagValue 

  def SetNpFloat128( self ):
    ### From original Infrastructure it append this np.float128
    ### Assuming it's not all Processor and Numpy framework that
    ### support this np.float128...
    try:
      self.TypeDict = '_NP_TYPE_CONV_DICT'
      self.IndexTypeDict=np.float128
      self.AddValueTypeDict = 'npy_float128' 
    except AttributeError:
      raise CCITypeSupportWarning, "np.float128 not supported in your Numpy module..."
    

  def SetTempDirCompilation( self ):
    self.TemporaryFile = NamedTemporaryFile( mode='w+', suffix='', prefix='np_inline-', dir='/tmp/' ,delete=True ) 
    self._PATH = os.path.expanduser('{}'.format( self._PATH ) )
    if not os.path.exists(self._PATH):
      os.makedirs(self._PATH)    

  def SetSystemTypeLib( self ):
    self.ContextOS = 'lib'

  def __init__( self, *args, **kargs):
    self.__dict__.update( kargs )


    try:
      for FuncLoader in self.__Loader__:
        getattr( self, FuncLoader )( )
    except CCITypeSupportWarning:
      print "System and/or Numpy version is not supporting the 128bit operation mode."
    

  def _mod_path( self ):
    ### Removed from Parameter : mod_name
    ### Proeprty self.FModName, ------ replace --> mod_name
    #StrValue=str( self.ContextOS )
    StrValue=str( self.ContextLibOs ) 
    return os.path.join( self._PATH, StrValue.format( self.FModName ) )


  def _import():
    ### Removed from Parameter :  mod_name
    ### property self.FModName, ------ replace --> mod_name
    mod = imp.load_dynamic( self.FModName, _mod_path( self.FModName ) )
    self._FUNCS[mod_name] = getattr( mod, self.VarDefFunction ) 

  def inline( self ):
    ### Removed following variables  from Function parameter:
    ### 
    ### self.FUniqueName        ------ replace --> unique_name, 
    ### args=(),                ------ become  --> self.args
    ### py_types=(),            ------ become  --> self.py_types
    ### np_types=(),            ------ become  --> self.np_types
    ### code=None,              ------ become  --> self.code
    ### code_path=None,         ------ become  --> self.code_path
    ### support_code=None,      ------ become  --> self.support_code
    ### support_code_path=None, ------ become  --> self.support_code_path
    ### extension_kwargs={},    ------ become  --> self.extension_kwargs
    ### return_type=None        ------ become  --> self.return_type
    
    # We first just try to run the code. This makes calling the code the 
    # second time the fastest thing we do. 
    try:
      return self._FUNCS[ self.FUniqueName ]( *self.args )
    except:
        pass
        
    # Next, we try to import the module and inline it again. This will make
    # calling the code the first time reasonably fast. 
    try:
        _import( self.FUniqueName )
        return self._FUNCS[ self.FUniqueName ]( *self.args )
    except:
        pass

    # Now we can be as slow as we'd like. We either have an error or the 
    # code isn't compiled. We'll try to compile the code and call the function
    # again.
    # Note that we are generating the code here if the module isn't found,
    # but we don't try to see if the code is already written to disk. This 
    # allows the debug inline code to easily delete the module code. 
    with _COMP_LOCK:
        ### code_str = _string_or_path(self.code, self.code_path)
        ### moved to _gen_code

        ### support_code_str = _string_or_path(support_code, support_code_path)
        ### moved to _gen_code_support
      
        ### Now _gen_code does not come with parameter, and it does not
        ### return, it diretly update the Skeleton .

        ### self.GenerateCode( ) will update self.VarDefSkeleton.
        ### 
        self.GenerateCode( )
        
        
        #c_code = _gen_code(unique_name, code_str, py_types, np_types, 
        #                   support_code_str, return_type)
        ### Now _build_install_module does not come with parameter. 
        # _build_install_module(c_code, unique_name, extension_kwargs)
        self._build_install_module()
        _import( self.FUniqueName )

    return self._FUNCS[ self.FUniqueName ]( *self.args )    

  def inline_debug( self ):
    """Same as inline, but the types of each argument are checked, and 
      the code is recompiled the first time this function is called. """
    ### Removed Variable in Parameter :
    ### self.FUniqueName        ------ replace --->  unique_name,
    ### args=(),                ------ become ---->  self.args
    ### py_types=(),            ------ become ---->  self.py_types
    ### np_types=(),            ------ become ---->  self.np_types
    ### code=None,              ------ become ---->  self.FCCode and not self.code
    ### a property is under evaluation to allow throwing and error if
    ### code_path is used instead. 
    ### code_path=None,         ------ become ---->  self.code_path
    ### support_code=None,      ------ become ---->  self.support_code
    ### support_code_path=None, ------ become ---->  self.support_code_path
    ### extension_kwargs={},    ------ become ---->  self.extension_kwargs
    ### return_type=None        ------ become ---->  self.return_type
      
      # Check args, py_types and np_types for iterability.
    ListCheckArg=[ 'args', 'py_types', 'np_types']
    for IterAttr in ListCheckArg:
      assert( getattr( np, 'iterable')( getattr( self, IterAttr ) ) )
      print "<!>Assert 1<!>"
      #np.iterable(self.args))
      #assert(np.iterable(self.py_types))
      #assert(np.iterable(self.np_types))

    # Check that code and code path aren't both None, or not None.
    assert self.FCCode is not None or self.code_path is not None
    print "<!>Assert 2<!>"
    assert not ( self.FCCode is not None and self.code_path is not None )
    print "<!>Assert 3<!>"

    # Check support_code and support_code_path aren't both given.
    assert not ( self.support_code is not None and self.support_code_path is not None )
    print "<!>Assert 4<!>"

    # Check paths if they are used. 
    if self.code_path is not None:
      assert ( os.path.exists( self.code_path ) )
      print "<!>Assert 5<!>"
        
    if self.support_code_path is not None:
      assert( os.path.exists( self.support_code_path ) )
      print "<!>Assert 6<!>"

    # Type check python arguments.
    for py_obj, ( py_type, c_name) in zip( self.args[ :len( self.py_types ) ], self.py_types ):
      assert isinstance( py_obj, py_type ), 'Type err: {0}'.format( c_name )
      print "<!>Assert 7<!>"
      assert py_type in ( int, float ), 'Bad type: {0}'.format( py_type )
      print "<!>Assert 8<!>"
        
    # Type check numpy arguments. 
    for np_obj, ( np_type, ndim, c_name ) in zip( self.args[ len(self.py_types):], self.np_types):
      assert np_obj.dtype == np_type, 'Type err: {0}'.format( c_name )
      print "<!>Assert 9<!>"
      assert np_obj.ndim == ndim, 'Bad dims: {0}'.format( c_name )
      print "<!>Assert 10<!>"

    # Type check the return type. 
    assert self.return_type in ( None, int, float )
    print "<!>Assert 11<!>"

    # If this is the first call to this function, delete the module to force
    # a recompilation. 
    if self.FUniqueName not in self._FUNCS and os.path.exists( self._mod_path(  ) ):
      os.unlink( _mod_path( ) )
    
    return self.inline( )

  ###############################################################################
  # Helper functions.                                                           #
  ###############################################################################
  def _string_or_path( self, code_str, code_path ):
      """Return either code_str if it is not None, or the contents in 
      code_path.
      """
      ReturnInformation = None 
      if code_str is not None:
        ReturnInformation=code_str
      
      if code_path is not None:
        FH=open(code_path, 'r+')
        ReturnInformation = FH.read()
        FH.close( )

      return ReturnInformation

  ###############################################################################
  # Building and installation.                                                  #
  ###############################################################################
  def _build_install_module( self ):
    # Save the current path so we can reset at the end of this function.
    curpath = os.getcwd() 
    mod_name_c = '{0}.c'.format( self.FModName )

    try:
      FH = open(os.path.join(self._PATH, mod_name_c), 'wb')
      # Write out the code.
      ### replacing self.FCCode by self.VarDefSkeleton
      ### At this step we should own a complete model
      ### and skeleton will become complete and ready
      ### to write-down to compile-it.
      ### FH.write( self.FCCode )
      FH.write( self.VarDefSkeleton )
      FH.close() 

      # Make sure numpy headers are included. 
      if 'include_dirs' not in self.extension_kwargs:
          self.extension_kwargs['include_dirs'] = []
      self.extension_kwargs['include_dirs'].append( np.get_include() )
          
      # Change to the code directory.
      os.chdir(self._PATH)

      # Create the extension module object. 
      ext = Extension( self.FModName, [ mod_name_c ], **self.extension_kwargs)

      # Clean.
      setup( ext_modules=[ext], script_args=['clean'])

      # Build and install the module here. 
      setup(ext_modules=[ext], 
            script_args=['install', '--install-lib={0}'.format( self._PATH )])

    finally:
        os.chdir(curpath)

BoolTestDictManagerAdd  = True 
BoolTestSkeletonMod     = True
BoolTestSkeletonTag     = True
BoolTestSkeletonAdd     = True
BoolTestCodeGeneration  = True
BoolTestCodeCompilation = True 

if __name__.__eq__( '__main__' ):
  Acode = CCodeInline( )
  BInlineCode=r'''printf( "Program #%i: Hello world.\n", i ) ;'''
  BCode = CCodeInline( args=(1, ), py_types=(( int, 'i'),)  )

  if BoolTestDictManagerAdd:
    ### Example of Adding a type inside Dict-Manager for type conversion 
    Acode.TypeDict = '_RETURN_FUNC_DICT'
    Acode.IndexTypeDict=list
    Acode.AddValueTypeDict = 'PyList_FromCSV' 
  if BoolTestSkeletonMod:
    ### Choosong Skeleton 0   
    Acode.SkeletonIndex = 0 
    ### Updating Skeleton 
    Acode.AddSkeleton
    ### Outputing The Skeleton 
    print Acode.VarDefSkeleton
    if BoolTestSkeletonTag:
      ### Inserting Fist Tag inside SkeletonTag property-infrastructure 
      Acode.IsSkeletonTag = '__INCLUDE_HEADER__'
      print "Current tag: {}".format( Acode.CurrentSkeletonTag )
      ### Testing if the Tag is present:
      print "Is Tag:{} is present inside Skeleton: {}".format(Acode.CurrentSkeletonTag , Acode.IsSkeletonTag )
      ### Now Tag is inside property-memory so we can start changing it.
      Acode.SkeletonChange = '#include <Python.h>'
      ### Updating the skeleton. 
      Acode.UpdateSkeleton
      ### Outputing The Skeleton 
      print "Showing Skeleton-0 modification"
      print Acode.VarDefSkeleton
    if BoolTestSkeletonAdd:
      ### Adding a Skeleton 1
      Acode.SkeletonIndex = 1
      Acode.AddSkeleton
      Acode.IsSkeletonTag = '__INCLUDE_HEADER__'
      Acode.SkeletonChange = '\n#include <Python.h>\n#include <numpy/arrayobject.h>'
      Acode.UpdateSkeleton
      print "Showing Skeleton-1 modification"
      print Acode.VarDefSkeleton
      ### Returning to Skeleton 0
      Acode.SkeletonIndex = 0
      print "Back to Skeleton-0\nShowing Skeleton-0 Code."
      print Acode.VarDefSkeleton
      ### ... And so on ...
    #Acode.
  if BoolTestCodeGeneration:
    print "Start Parsing example with BoolTestCodeGeneration"
    BCode.SkeletonIndex = 1
    BCode.AddSkeleton
    BCode.FCCode = BInlineCode
    BCode.FUniqueName = 'hello_world_example'
    BCode.GenerateCode()
    print BCode.VarDefSkeleton
    if BoolTestCodeCompilation:
      ### re-writing the skeleton, BCode.GenerateCode() work-well, but path of inline or inline_debug are
      ### expecting having to parse the Skeleton...
      BCode.SkeletonIndex = 1
      BCode.AddSkeleton
      BCode.FUniqueName = 'hello_world_example'
      BCode.IncludeHeaderType = 'internal'
      BCode.DictIncludeHeader = 'stdlib.h'
      BCode.UpdateIncludeHeader
      BCode.GenerateCode()
      #BCode.inline_debug( )
