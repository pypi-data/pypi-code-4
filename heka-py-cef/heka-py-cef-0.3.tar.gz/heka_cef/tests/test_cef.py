# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2012
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Victor Ng (vng@mozilla.com)
#
# ***** END LICENSE BLOCK *****
from heka.config import client_from_text_config
import heka_cef
from heka.tests.helpers import decode_message
import unittest
from cef import logger
from nose.tools import raises, eq_
from heka_cef.cef_plugin import InvalidArgumentError


class TestHeka(unittest.TestCase):
    logger = 'tests'

    def setUp(self):

        cfg_txt = """
        [heka]
        stream_class = heka.streams.DebugCaptureStream

        [heka_plugin_cef]
        provider=heka_cef.cef_plugin:config_plugin
        """
        ###
        self.client = client_from_text_config(cfg_txt, 'heka')

        self.environ = {'REMOTE_ADDR': '127.0.0.1', 'HTTP_HOST': '127.0.0.1',
                        'PATH_INFO': '/', 'REQUEST_METHOD': 'GET',
                        'HTTP_USER_AGENT': 'MySuperBrowser'}

        self.config = {'cef.version': '0', 'cef.vendor': 'mozilla',
                       'cef.device_version': '3', 'cef.product': 'weave',
                       'cef': True}

        self._warn = []

        def _warning(warn):
            self._warn.append(warn)

        self.old_logger = logger.warning
        logger.warning = _warning

    def tearDown(self):
        logger.warning = self.old_logger

    def test_setup_extensions(self):
        assert hasattr(self.client, 'cef')

    def _log(self, name, severity, *args, **kw):
        # Capture the output from heka and clear the internal debug buffer
        self.client.cef(name, severity, self.environ, self.config, *args, **kw)
        msgs = self.client.stream.msgs

        # Need to strip out protobuf header of 8 bytes
        h, msg = decode_message(msgs[0])

        msgs.clear()
        # We only care about the CEF payload
        assert msg.type == 'cef'
        return msg.payload

    def test_cef_logging(self):
        # should not fail
        res = self._log('xx|x', 5)
        self.assertEquals(len(res.split('|')), 10)

        # should not fail and be properly escaped
        self.environ['HTTP_USER_AGENT'] = "=|\\"
        content = self._log('xxx', 5)

        cs = 'cs1Label=requestClientApplication cs1=\=|\\\\ '
        self.assertTrue(cs in content)

        # should log.warn because extra keys shouldn't have pipes
        self._log('xxx', 5, **{'ba|d': 1})

        self.assertEqual('The "ba|d" key contains illegal characters',
                         self._warn[0])

    def test_suser(self):
        content = self._log('xx|x', 5, username='me')
        self.assertTrue('suser=me' in content)

    def test_custom_extensions(self):
        content = self._log('xx|x', 5, username='me',
                            custom1='ok')
        self.assertTrue('custom1=ok' in content)

    def test_too_big(self):
        big = 'i' * 500
        bigger = 'u' * 550
        content = self._log('xx|x', 5, username='me',
                            custom1='ok', big=big, bigger=bigger)
        self.assertTrue('big=ii' in content)
        self.assertFalse('bigger=uu' in content)
        self.assertTrue('CEF Message too big' in self._warn[0])

    def test_conversions(self):
        content = self._log('xx\nx|xx\rx', 5, username='me',
                            ext1='ok=ok', ext2='ok\\ok')
        self.assertTrue('xx\\\nx\\|xx\\\rx' in content)
        self.assertTrue("ext1=ok\\=ok ext2=ok\\\\ok" in content)

    def test_default_signature(self):
        content = self._log('xx', 5)
        self.assertTrue('xx|xx' in content)

    def test_use_of_constant(self):
        content = self._log('xx', 5,
                signature=heka_cef.AUTH_FAILURE)
        assert '|AuthFail|' in content


class TestExtraConfig(unittest.TestCase):

    logger = 'tests'

    def test_config(self):

        cfg_txt = """
        [heka]
        stream_class = heka.streams.DebugCaptureStream

        [heka_plugin_cef]
        provider=heka_cef.cef_plugin:config_plugin
        syslog_facility=KERN
        syslog_ident=some_identifier
        syslog_priority=EMERG
        """
        client = client_from_text_config(cfg_txt, 'heka')
        expected = {'syslog_priority': 'EMERG',
                    'syslog_ident': 'some_identifier',
                    'syslog_facility': 'KERN'}
        eq_(client.cef.cef_meta, expected)

    def test_missing_syslog_options_not_null(self):
        cfg_txt = """
        [heka]
        stream_class = heka.streams.DebugCaptureStream

        [heka_plugin_cef]
        provider=heka_cef.cef_plugin:config_plugin
        """
        client = client_from_text_config(cfg_txt, 'heka')
        expected = {'syslog_priority': '',
                    'syslog_ident': '',
                    'syslog_facility': 'LOCAL4',}
        eq_(client.cef.cef_meta, expected)
