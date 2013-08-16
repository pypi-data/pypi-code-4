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
logging.getLogger('pika').setLevel(logging.CRITICAL)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'node_modules'))
from event_amd.event_amd import EventEmitter

class Message:
    def __init__( self, _config = {}, listener = None, start_message = None ):
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

        connection = pika.BlockingConnection( parameters = connection_parameters )
        #TODO: pika.adapters.select_connection.SelectConnection( parameters=parameters, on_open_callback=on_open )
        # https://pika.readthedocs.org/en/latest/examples/comparing_publishing_sync_async.html
        return connection

    def listen( self, server, callback, exchange_name='', exchange_type = 'direct', queue_name ='' ):
        connection = self.getConnection( server, False )
        channel = connection.channel()
        
        channel.basic_qos(prefetch_count=1)
        if queue_name == '' :
            result = channel.queue_declare(exclusive=True)
            queue_name = result.method.queue
            #print 'Have: ',( queue_name )
        else :
            channel.queue_declare( queue=queue_name, durable=True )
        if exchange_name != '' :
            channel.exchange_declare( exchange=exchange_name, type=exchange_type, durable=True )
            channel.queue_bind(exchange=exchange_name, queue=queue_name )
        channel.basic_consume( callback, queue = queue_name )
        channel.start_consuming()

    def writeToExchange( self, server, exchange_name, exchange_type = 'direct', queue_name='', message='' ):
        print 'writeToExchange:'+queue_name
        connection = pika.BlockingConnection(pika.ConnectionParameters( host='localhost' ))
        channel = connection.channel()
        if exchange_name != '' :
            print exchange_name, exchange_type
            channel.exchange_declare( exchange=exchange_name, type=exchange_type, durable=True )
        channel.basic_publish( exchange=exchange_name, routing_key=queue_name, body=message, properties=pika.BasicProperties(
            delivery_mode = 2#make message persistent
        ))
        connection.close() 

    def getListener( self ):
        return self.listener;
