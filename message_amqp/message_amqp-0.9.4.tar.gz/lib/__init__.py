#! /usr/bin/env python
#        \file message.py
#  
#        \author borrey
# 
#        Date Created: 2013-06-12T12:03:03-0600\n
#        Date Modified:
# 
#        Copyright  All Rights Reserved

import sys, os, pika, logging
from threading import Thread
from event_amd.event_amd import EventEmitter

logging.getLogger('pika').setLevel(logging.CRITICAL)

class _MessageListener( Thread ):
    def __init__( self, server, callback, exchange_name='', exchange_type = 'direct', queue_name ='' ) :
        self.stop_flag = False
        self.connection = None
        self.queue_name = queue_name
        self.callback = callback
        self.exchange_type = exchange_type
        self.exchange_name = exchange_name
        self.connection_parameters = self.getConnection( server )
        Thread.__init__(self)
            
    def run( self ):
        def on_connected( new_connection ):
            self.connection = new_connection
            self.openChannel()
        self.poll_connection = pika.SelectConnection( parameters=self.connection_parameters, on_open_callback=on_connected ) 
        def timeout():
            if self.stop_flag :
                self.stop()
            else:
                self.poll_connection.add_timeout( 5, timeout )
        self.poll_connection.add_timeout( 5, timeout )
        self.poll_connection.ioloop.start()

    def setStopFlag( self, stop=True ):
        self.stop_flag = stop

    def stop( self ):
        self.poll_connection.close()

    def bindExchange( self ):
        def on_queue_bind( *args ) :
            self._consumer_tag = self.channel.basic_consume( self.callback, queue =self.queue_name )
        self.channel.queue_bind( on_queue_bind, exchange=self.exchange_name, queue=self.queue_name )
        
    def bindQueue ( self ):
        def on_exchange_declared( *args ):
            self.bindExchange()
        if self.exchange_name != '' :
            self.channel.exchange_declare( on_exchange_declared, exchange=self.exchange_name, type=self.exchange_type, durable=True )
        else :
            self._consumer_tag = self.channel.basic_consume( self.callback, queue = self.queue_name )
    def setupQueue( self ) :
        def on_queue_declared( frame ):
            self.bindQueue()
        self.channel.queue_declare( on_queue_declared, queue=self.queue_name, durable=True )

    def openChannel( self ) :
        def on_channel_open( channel ):
            self.channel = channel
            self.channel.basic_qos( prefetch_count=1 )
            self.setupQueue()
        self.connection.channel(on_channel_open)

    def getConnection( self, server ) :
        if 'login' in server :
            login = server['login']
        else :
            login = 'guest'
        if 'password' in server :
            password = server['password']
        else :
            password = 'guest'

        credentials = pika.PlainCredentials( login, password )

        if 'host' in server :
            host = server['host']
        else :
            host = 'localhost'
        if 'port' in server :
            port = server['port']
        else :
            port = 5672
        if 'vhost' in server :
            vhost = server['vhost']
        else :
            vhost = '/'
        connection_parameters = pika.ConnectionParameters( host=host, port=port, virtual_host=vhost, credentials=credentials )#TODO:ssl_options
        return connection_parameters


class Message:
    def __init__( self, _config = {}, listener = None, start_message = None ):
        self._threads = []
        self._handlers = []
        self._keep_running = True
        if listener is None:
            self.listener = EventEmitter()
        else:
            self.listener = listener

        if 'server' in  _config :
            self.server = _config['server']
        else :
            self.server = { 'host' : 'localhost', 'defaultExchangeName' : 'amqp_exchange', 'port' : 5672, 'virtual_host' : '/', 'login': 'guest', 'password': 'guest' }

        if 'exchange' in  _config :
            self.exchange = _config['exchange']
        else :
            self.exchange = ''

        if 'exchange_type' in  _config :
            self.exchange_type = _config['exchange_type']
        else :
            self.exchange_type = 'direct'

        if 'queue' in  _config :
            self.queue = _config['queue']
        else :
            self.queue = ''
        if start_message is not None :
            def emitMessage( ch, method, properties, body ):                
                ch.basic_ack(delivery_tag = method.delivery_tag)
                self.listener.emit( 'message', body )
            def callback( *args) :
                #try :
                self.listen( self.server, emitMessage, self.exchange, self.exchange_type, self.queue )
            self.listener.on( start_message, callback )
        self.listener.on('stop', self.handleKeyboardInterrupt )
        
    def handleKeyboardInterrupt( self ) :
        for t in self._threads:
            t.setStopFlag( True )

    def getConnection( self, server, blocking ) :

        if 'login' in server :
            login = server['login']
        else :
            login = 'guest'
        if 'password' in server :
            password = server['password']
        else :
            password = 'guest'

        credentials = pika.PlainCredentials( login, password )

        if 'host' in server :
            host = server['host']
        else :
            host = 'localhost'
        if 'port' in server :
            port = server['port']
        else :
            port = 5672
        if 'vhost' in server :
            vhost = server['vhost']
        else :
            vhost = '/'
        connection_parameters = pika.ConnectionParameters( host=host, port=port, virtual_host=vhost, credentials=credentials )#TODO:ssl_options
        return connection_parameters

    def listen( self, server, callback, exchange_name='', exchange_type = 'direct', queue_name ='', blocking=False ):
        message_listener = _MessageListener( server, callback, exchange_name, exchange_type, queue_name )
        #try :
        #    message_listener.run()
        #except KeyboardInterrupt:
        #    # Gracefully close the connection
        #    message_listener.stop()
        #self._threads.extend( message_listener )
        self._threads.append( message_listener )
        message_listener.start()
        
    def writeToExchange( self, server, exchange_name, exchange_type = 'direct', queue_name='', message='' ):
        connection = pika.BlockingConnection(pika.ConnectionParameters( host='localhost' ))
        channel = connection.channel()
        if exchange_name != '' :
            channel.exchange_declare( exchange=exchange_name, type=exchange_type, durable=True )
        channel.basic_publish( exchange=exchange_name, routing_key=queue_name, body=message, properties=pika.BasicProperties(
            delivery_mode = 2#make message persistent
        ))
        connection.close() 

    def getListener( self ):
        return self.listener;
