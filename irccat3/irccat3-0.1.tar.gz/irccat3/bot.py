import irc.client
import logging
import sys
import threading
import time
import Queue

import listener

log = logging.getLogger(__name__)


class IRCCat(irc.client.SimpleIRCClient):
    def __init__(self, target, q, l):
        irc.client.SimpleIRCClient.__init__(self)
        self.target = target
        self.q = q

        self.l = l

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, connection, event):
        if irc.client.is_channel(self.target):
            connection.join(self.target)
        else:
            self.process_loop()

    def on_join(self, connection, event):
        self.process_loop()

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def process_loop(self):
        while 1:
            self.ircobj.process_once()
            try:
                self.l.wait_and_handle(0.5)
                if self.q.empty():
                    continue
                line = self.q.get()
            except Queue.Empty:
                log.debug('No msg')
                continue
            self.connection.privmsg(self.target, line)
        self.connection.quit("Using irc.client.py")

