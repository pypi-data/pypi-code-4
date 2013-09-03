

# class PatchedTornadoConnection(TornadoConnection):
#     r"""Patching TornadoConnection class, because reconnection strategy of
#     `TornadoConnection` does not work. `_handle_disconnect` hook method
#     should only remove_handler rather than close the loop.
#      .. document private functions
#      .. automethod:: _handle_disconnect
#     """

#     def _handle_disconnect(self):
#         r"""hook method that called internally when we know our socket is
#         disconnected already.

#         See Also
#         --------
#         IOLoop.add_timeout :
#             `Pika documentation
#             <https://pika.readthedocs.org/en/latest/adapters.html#tornadoconnection>`_

#         Notes
#         -----
#         We override this method, because it closes the loop which leads to
#         brocken connection between rabbit client and server. We tried to
#         overcome this, by removing handler from disconnected client socket.

#         """
#         pika.log.info("Patched handler is called")
#         # remove socket handler
#         self.ioloop.remove_handler(self.socket.fileno())
#         # close connection state
#         self._on_connection_closed(None, True)


# class BaseAMQPConnection(object):
#     r"""Patching TornadoConnection class, because reconnection strategy of
#     `TornadoConnection` does not work. `_handle_disconnect` hook method
#     should only remove_handler rather than close the loop.
#      .. document private functions

#      Methods
#      -------
#      .. automethod:: _reconnect
#     """

#     queue_name = '{}_{}'.format(ns.EXCHANGE_NAME, ns.RABBITMQ_HOST)

#     def _reconnect(self):
#         """
#         responsible for reconnecting a client to a server.

#         Notes
#         -----
#         `_reconnect()` is a hook method, which is called internally by
#         `connect()` if socket connection has been closed.
#         """
#         log.debug('reconnecting....')
#         # add consumer to ioloop and connecting
#         add_timeout(.4, self.connect)

#     @property
#     def exchange(self):
#         r"""
#         is a property

#         Returns
#         -------
#         ns.EXCHANGE_NAME : a RabbitMQ exchange name
#         """
#         return ns.EXCHANGE_NAME

#     @property
#     def properties(self):
#         r"""
#         is a property

#         Returns
#         -------
#         pika.BasicProperties : global properties that define content_type,
#         delivery_mode...
#         """

#         properties = pika.BasicProperties(content_type='application/json',
#                                           delivery_mode=2)
#         return properties

#     @property
#     def io_loop(self):
#         r"""
#         is a property

#         Returns
#         -------
#         ioloop.IOLoop : level-triggered Tornado IOLoop
#         """

#         return tornado.ioloop.IOLoop.instance()

#     def __init__(self):
#         r"""
#         initializes an instance of BaseAMQPConnection with a lot of properties
#         """
#         self.connection = None
#         self.channel = None
#         self.connected = False
#         self.connecting = False
#         log.debug('Rabbit consumer initialized!')
#         # for reconnecting strategy
#         self.multiplier = 1.30
#         self.timeout_delay = 500
#         self.max_delay = 30000.0

#     def connect(self):
#         """
#         Creates new `PatchedTornadoConnection` with specified `host` and `port`.

#         Notes
#         -----
#         This method is generally responsible for:
#           #. connecting to RabbitMQ server
#           #. catching closing connections and reconnecting with reconnection
#              strategy
#         """
#         log.debug("connecting")
#         param = pika.ConnectionParameters(
#                 host=ns.RABBITMQ_HOST,
#                 port=ns.RABBIT_PORT
#         )
#         try:
#             self.connection = PatchedTornadoConnection(\
#                 param,
#                 on_open_callback=self.on_connected)
#             # patch to reconnect
#             self.connection.add_on_close_callback(self.on_close)
#             self.connecting = True
#         except socket.error, e:
#             log.debug('socket_error {} '.format(e))
#             self.io_loop.add_callback(self._reconnect)

#     def on_cancel(self):
#         pika.log.info("Client has gone. Queue is ok.")

#     def on_close(self, connection):
#         r"""
#         Trying to close normally and reconnects with new `timeout_delay`

#         Parameters
#         ----------
#         connection : PatchedTornadoConnection
#             connection instance.
#         """
#         log.debug('Connection closed, trying reconnect in 5 seconds')
#         self.connecting = self.connected = False
#         # todo: reconnection strategy
#         t = min(self.max_delay, self.timeout_delay)
#         self.timeout = self.timeout_delay * self.multiplier
#         add_timeout(t, self.connect)

#     def finish(self, result, error):
#         r"""
#         finish is callback of asynchronously called functions, which have
#         callback as a keyword attribute.

#         Parameters
#         ----------
#         result : any type
#             contains the result of asynchronously executed function.
#         error: Exception
#             raised exception

#         Notes
#         -----
#         handles error by re-raising it or simply returns result
#         """
#         if error:
#             log.debug('Exception when trying to listen')
#             raise error
#         log.debug('starting listening')
#         return result

#     @tornado.gen.engine
#     def init_brocker_jobs(self):
#         """
#         method which dictates the connection needs:
#           * consumer - go to listen mode
#           * publisher - infinite callback to publish somewhere
#           * brocker - both consumer and publisher

#         Notes
#         -----
#         Override this method to specify client's jobs
#         """
#         pass
