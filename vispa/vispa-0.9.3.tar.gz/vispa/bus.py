# -*- coding: utf-8 -*-

# imports
import vispa
import cherrypy
from time import time, sleep
from threading import Thread
import json

# use websockets?
USE_SOCKETS = vispa.config('websockets', 'enabled', False)
# subscribers stored as {sessionid: Publisher}
SUBSCRIBERS = {}
# a dict, userid -> sessionids (list)
USERSESSIONS = {}
# a dict, sessionid -> userid
SESSIONOWNERS = {}
# timestamps only for PollingPublishers to handle
# the deletion of their entry in SUBSCRIBERS
# (SocketPublishers are removed automatically)
TIMESTAMPS = {}

# add function
def add_session(sessionid, userid, publisher):
    # add SUBSCRIBERS entry
    SUBSCRIBERS[sessionid] = publisher
    # add TIMESTMAPS entry?
    if isinstance(publisher, PollingPublisher):
        TIMESTAMPS[sessionid] = int(time())
    # add USERSESSIONS entry
    if userid not in USERSESSIONS.keys():
        USERSESSIONS[userid] = []
    if sessionid not in USERSESSIONS[userid]:
        USERSESSIONS[userid].append(sessionid)
    # add SESSIONOWNERS entry
    SESSIONOWNERS[sessionid] = userid

# remove function
def remove_session(sessionid):
    # remove from SUBSCRIBERS
    if sessionid in SUBSCRIBERS.keys():
        del SUBSCRIBERS[sessionid]
    # remove from SESSIONOWNERS
    if sessionid in SESSIONOWNERS.keys():
        userid = SESSIONOWNERS[sessionid]
        # remove from USERSESSIONS
        if userid in USERSESSIONS.keys():
            USERSESSIONS[userid].remove(sessionid)
            if not len(USERSESSIONS[userid]):
                del USERSESSIONS[userid]
        # delete the entry in SESSIONOWNERS
        del SESSIONOWNERS[sessionid]
    if sessionid in TIMESTAMPS.keys():
        # delete the timestamp
        del TIMESTAMPS[sessionid]

# options for the CleanerThread
# this has to be a dict, since elementary
# datatypes don't live in the shared memory
CLEANEROPTIONS = {'RUN': True,
                  'DELAY': 5,
                  'MAXDIFF': 10}
class CleanerThread:

    def __init__(self):
        while CLEANEROPTIONS['RUN']:
            for sessionid, stamp in TIMESTAMPS.items():
                if int(time()) - stamp > CLEANEROPTIONS['MAXDIFF']:
                    # delete the publisher and all its data
                    remove_session(sessionid)
            sleep(CLEANEROPTIONS['DELAY'])

class Bus:

    def __init__(self):
        # pub/sub data storage
        self.handlers = {}
        # configure and start the cleaner thread
        cleaner = Thread(target=CleanerThread, name='BusPollingCleaner')
        cleaner.daemon = True
        cherrypy.engine.subscribe('stop', self._stop_cleaner)
        cleaner.start()

    def _stop_cleaner(self):
        CLEANEROPTIONS['RUN'] = False

    def send(self, sessionid=None, userid=None, except_sids=[], payload=None, binary=False):
        # sessionid is preferred wrt userid
        if sessionid:
            sessionid = unicode(sessionid)
            if sessionid in SUBSCRIBERS.keys():
                SUBSCRIBERS[sessionid].send(json.dumps(payload), binary=binary)
        elif userid:
            userid = unicode(userid)
            if userid in USERSESSIONS.keys():
                if not isinstance(except_sids, list):
                    except_sids = [except_sids]
                for sid in USERSESSIONS[userid]:
                    if sid in except_sids:
                        continue
                    SUBSCRIBERS[sid].send(json.dumps(payload), binary=binary)

    def sendtopic(self, topic, sessionid=None, userid=None, except_sids=[], payload=None, binary=False):
        payload = payload or {}
        if not isinstance(payload, dict):
            payload = {'payload': payload}
        payload['topic'] = topic
        self.send(sessionid=sessionid, userid=userid, except_sids=except_sids, payload=payload, binary=binary)

    def received_message(self, msg, sessionid):
        # json?
        try:
            data = json.loads(str(msg))
        except:
            data = None
        # atm, we cannot do anything when the msg
        # is not json parsable or has no key 'topic'
        if not data or not 'topic' in data.keys():
            return
        # sessionid has to be set for safety reasons
        if not sessionid:
            return
        self.publish(data['topic'], sessionid, payload=data)

    def publish(self, topic, sessionid, payload=None):
        if topic in self.handlers.keys():
            # userid?
            userid = None
            if sessionid in SESSIONOWNERS.keys():
                userid = SESSIONOWNERS[sessionid]
            for handler in self.handlers[topic]:
                handler(sessionid=sessionid, userid=userid, payload=payload)

    def subscribe(self, topic, handler):
        if topic not in self.handlers.keys():
            self.handlers[topic] = []
        self.handlers[topic].append(handler)

    def unsubscribe(self, topic, handler):
        if topic in self.handlers.keys():
            if handler in self.handlers[topic]:
                self.handlers[topic].remove(handler)

bus = Bus()

class SocketPublisher:
    pass
if USE_SOCKETS:
    from ws4py.websocket import WebSocket

    class SocketPublisher(WebSocket):

        def __init__(self, *args, **kwargs):
            WebSocket.__init__(self, *args, **kwargs)
            # self.platform is set in the WSTool right after 'upgrade'
            self.platform = None
            # self.sesseionid and self.userid are set in 'socket_hook'
            # in the bus controller
            self.sessionid = None
            self.userid = None

        def store(self):
            if self.sessionid:
                add_session(self.sessionid, self.userid, self)

        def closed(self, code, reason=None):
            remove_session(self.sessionid)

        def received_message(self, msg):
            if self.platform:
                self.platform.bus.received_message(msg, self.sessionid)


class PollingPublisher:

    def __init__(self, sessionid):
        self.sessionid = sessionid
        self._stack = []

    def send(self, payload, binary=False):
        self._stack.append(payload)
        # TODO: implement binary payloads

    def fetch(self, n=0):
        stack = []
        if not n or n > len(self._stack):
            stack = self._stack
            self._stack = []
        else:
            stack = self._stack[:n]
            self._stack = self._stack[n:]
        return stack

    def received_message(self, msg):
        if self.platform:
            bus.received_message(msg, self.sessionid)



