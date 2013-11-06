# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from twisted.internet import interfaces
from twisted.test.proto_helpers import MemoryReactor
from twisted.trial import unittest

from txi2p.bob.endpoints import (BOBI2PClientEndpoint,
                                 BOBI2PServerEndpoint)


class BOBI2PClientEndpointPluginTest(unittest.TestCase):
    """
    Unit tests for the BOB I2P client endpoint description parser.
    """

    _parserClass = twisted.plugins.txi2p._BOBI2PClientParser

    def test_pluginDiscovery(self):
        parsers = list(getPlugins(
            interfaces.IStreamClientEndpointStringParserWithReactor))
        for p in parsers:
            if isinstance(p, self._parserClass):
                break
        else:
            self.fail(
                "Did not find BOBI2PClientEndpoint parser in %r" % (parsers,))

    def test_interface(self):
        parser = self._parserClass()
        self.assertTrue(verifyObject(
            interfaces.IStreamClientEndpointStringParserWithReactor, parser))

    def test_stringDescription(self):
        ep = clientFromString(
            MemoryReactor(), "i2pbob:stats.i2p:tunnelNick=spam:inport=12345")
        self.assertIsInstance(ep, BOBI2PClientEndpoint)
        self.assertIsInstance(ep._reactor, MemoryReactor)
        self.assertEqual(ep._dest,"stats.i2p")
        self.assertEqual(ep._tunnelNick,"spam")
        self.assertEqual(ep._inport,12345)
