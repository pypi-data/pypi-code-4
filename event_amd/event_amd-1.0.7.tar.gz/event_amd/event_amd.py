#! /usr/bin/env python
#        \file event_amd.py
#  
#        \author borrey
# 
#        Date Created: 2013-06-12T14:10:01-0600\n
#        Date Modified:
# 
#        Copyright  All Rights Reserved
import sys
class EventEmitter:
    def __init__( self ):
        self._events  = {}
        self.defaultMaxListeners = 10
        self.setMaxListeners( self.defaultMaxListeners )

    def setMaxListeners( self, n ):
        if (int(n) or n.isdigit()) and n < 0 :
            self._maxListeners = n

    def emit( self, *args ):
        arg_len = len(args)
        iterargs = iter(args)
        if self._events is None:
            self._events  = {}
        if arg_len < 1 :
            sys.stderr.write('arguments too short')
        else:
            emit_type = next( iterargs )
            arg_len = []
            for arg in iterargs :
                arg_len.append( arg )
            if emit_type=='error':
                if emit_type not in self._events:
                    raise Exception('bus error')
                    return None
            if emit_type in self._events :
                emit_handler = self._events[emit_type]
                if hasattr( emit_handler, '__call__' ) :
                    emit_handler( *arg_len )
                else :
                    for listener in emit_handler :
                        listener( *arg_len )
                return True
            else :
                return None
            
    def addListener( self, _type, _listener ):
        if self._events is None:
            self._events  = {}
        if _type in self._events:
            listeners = self._events[ _type ]
            if hasattr( listeners, '__call__') :
                listener_array = [ listeners, _listener ]
                self._events[ _type ] = listener_array
            else :
                listeners.append( _listener )
                if self._maxListeners < len( listeners ):
                    sys.stderr.wite('(Python) warning: possible EventEmitter memory leak detected. '
                                    +len( listeners )+' listeners added. '+self._maxListeners+' max. '
                                    +'Use emitter.setMaxListeners() to increase limit.')
        else :
            self._events[ _type ] = _listener


    def on( self, _type, _listener ):
        self.addListener( _type, _listener )

    #def once( self, _type, _listener ):
        
    def removeListener( self, _type, _listener ):
        if self._events is None:
            self._events  = {}
        if hasattr( _listener, '__call__') :
            if self._events is not None and _type in self._events:
                listeners = self._events[ _type ]
                if hasattr( listeners, '__call__') and listeners == _listener :
                    del self._events[ _type ]
                elif type(listeners) == list :
                    for listener in listeners :
                        if listener == _listener :
                            listeners.remove( listener )
                return self
            else :
                return self
        else :
            raise Exception('listener must be a function')
