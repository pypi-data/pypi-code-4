# -*- coding: utf-8 -*-
import logging
import unittest

import mock

import log

# For OSX, you want a lower number for the tests.
@mock.patch.object(log, 'MAX_SIZE', 2000)
class TestErrorLog(unittest.TestCase):

    def setUp(self):
        self.log = logging.getLogger('test.logging')
        self.log.addHandler(log.UnicodeHandler())

    @mock.patch('log.UnicodeHandler.emitted')
    def test_called(self, emitted):
        self.log.error('blargh!')
        assert emitted.called

    @mock.patch('log.UnicodeHandler.emitted')
    def test_large(self, emitted):
        self.log.error('*' * (log.MAX_SIZE + 10))
        assert emitted.called

    @mock.patch('log.UnicodeHandler.emitted')
    def test_unicode(self, emitted):
        self.log.error(u'نصرت فتح علی خان')
        assert emitted.called


if __name__=='__main__':
    unittest.main()
