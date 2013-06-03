# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
from vispa.controller import AbstractController
from vispa.bus import SocketPublisher, PollingPublisher, USE_SOCKETS, SUBSCRIBERS, \
USERSESSIONS, SESSIONOWNERS, TIMESTAMPS, add_session
from time import time
import json


class BusController(AbstractController):

    @cherrypy.expose
    def index(self, *args, **kwargs):
        pass

    def get_pollingpublisher(self, session_id, user_id):
        if session_id in SUBSCRIBERS.keys():
            publisher = SUBSCRIBERS[session_id]
            if not isinstance(publisher, PollingPublisher):
                return None
        else:
            publisher = PollingPublisher(session_id)
            add_session(session_id, user_id, publisher)
        return publisher

    @cherrypy.expose
    @cherrypy.tools.workspace(on=False)
    @cherrypy.tools.json_out()
    @cherrypy.tools.allow(methods=["POST"])
    def poll(self, *args, **kwargs):
        session_id = self.get('session_id')
        user_id = self.get('user_id')
        publisher = self.get_pollingpublisher(session_id, user_id)
        if not isinstance(publisher, PollingPublisher):
            return ''
        TIMESTAMPS[session_id] = int(time())
        stack = publisher.fetch()
        return stack

    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.allow(methods=["POST"])
    def receive(self, *args, **kwargs):
        # msg is the first key of kwargs
        msg = kwargs.keys()[0]
        session_id = cherrypy.session.id
        user_id = self.get('user_id')
        publisher = self.get_pollingpublisher(session_id, user_id)
        if isinstance(publisher, PollingPublisher):
            publisher.received_message(msg)


# overwrite the BusController's index?
if USE_SOCKETS:
    @cherrypy.expose
    @cherrypy.tools.user()
    @cherrypy.tools.websocket(handler_cls=SocketPublisher)
    def socket_hook(self, *args, **kwargs):
        # the user is connected via this controller function
        # on startup, so store user_id<->session_id information
        # in the publisher at 'cherrypy.serving.request.ws_handler'
        publisher = cherrypy.serving.request.ws_handler
        setattr(publisher, 'session_id', cherrypy.session.id)
        setattr(publisher, 'user_id', self.get('user_id'))
        # call the publisher's 'store' method to register it to the bus
        publisher.store()

    BusController.index = socket_hook