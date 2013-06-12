#!/usr/bin/env python3
"""
TEST.IO.TEST_CHAT_REPLIES.PY -- test script for chat_replies module
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the chat_replies module of
plib.io.
"""

import unittest

import plib.io.classes  # FIXME: why is this needed to make things work?

from plib.io.mixins import EchoRequestMixin
from plib.io.async import PersistentRequestHandler, SocketServer
from plib.io.classes import chat_replies

from .testlib import IOServerMixin, IOChannelTest


class ChatHandler(EchoRequestMixin, PersistentRequestHandler):
    pass


class ChatServer(IOServerMixin, SocketServer):
    pass


class ChatTestMixin(object):
    
    handler_class = ChatHandler
    server_class = ChatServer


class ChatClientTest(ChatTestMixin, IOChannelTest, unittest.TestCase):
    
    def test_chat_client(self):
        seq = [b"Python rocks!", b"Try it today!", b"You'll be glad you did!"]
        results = [reply for reply in chat_replies(
            ('localhost', self.server_port), seq)]
        self.assertEqual(results, seq)


def testcallback():
    pass


class ChatClientTestCallback(ChatTestMixin, IOChannelTest, unittest.TestCase):
    
    def test_chat_callback(self):
        seq = [b"You betcha!", b"It's *much* better than Perl!", b"And don't even *mention* C++!"]
        results = [reply for reply in chat_replies(
            ('localhost', self.server_port), seq, testcallback)]
        self.assertEqual(results, seq)


start_msg = b"Started!"


class ChatHandlerNone(ChatHandler):
    
    def __init__(self, request, client_address, server):
        ChatHandler.__init__(self, request, client_address, server)
        self.start(start_msg)


class ChatClientTestWithNone(ChatTestMixin, IOChannelTest, unittest.TestCase):
    
    handler_class = ChatHandlerNone
    
    def test_chat_client(self):
        seq = [None, b"Python rocks!", b"Try it today!", b"You'll be glad you did!"]
        results = [reply for reply in chat_replies(
            ('localhost', self.server_port), seq)]
        self.assertEqual(results, [start_msg] + seq[1:])


if __name__ == '__main__':
    unittest.main()
