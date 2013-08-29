#! /usr/bin/env python
#        \file Component.py
#  
#        \author borrey
# 
#        Date Created: 2013-06-04T16:48:41-0600\n
#        Date Modified:
# 
#        Copyright  All Rights Reserved
import sys
from message_amqp import Message
from event_amd.event_amd import EventEmitter
from time import sleep

class BusComponent:

    CONSUME_STATE = 1
    SEND_STATE = 2

    def __init__( self, bus_server, bus_listener, bus_emit, initial_state=CONSUME_STATE, verbose=False ) :
        self.event_listener = EventEmitter()
        self.state = initial_state
        self.verbose = verbose
        self.message = Message( {
            'server' :  bus_server,
            'exchange' : bus_listener['exchange'], 'queue' : bus_listener['queue']
        }, self.event_listener, 'start' )
        
        self.event_listener.on( 'message', self.messageHandler )

    def messageHandler ( self, message ) :
        #TODO
        sys.stderr.write('messageHandler %s\n' % message)

    def runComponent( self ) :
        try :
            self.event_listener.emit('start')
            while True :
                if self.state == self.CONSUME_STATE :
                    self.consumeState()
                elif self.state == self.LISTEN_STATE :
                    self.listenState()
                else :
                    sys.stderr.write( 'unknown state' )
        except ( KeyboardInterrupt, SystemExit ):
            self.event_listener.emit( 'stop' )
    def setState( self, state ):
        #This class is to set the state
        #put it here so that I can access it from outside the class (mostly for testing)
        self.state = state


    def consumeState( self ):
        #this state is to receive commands and resources needed 
        #log amqp
        #
        #Get possible resources. get instructions
        print 'consumeState'
        sleep(10)
    
    def listenState( self ):
        print 'listenState'
        sleep(10)
