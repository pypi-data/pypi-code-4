# coding: utf-8
from unittest import TestCase
from grab import Grab, DataNotFound

from .util import GRAB_TRANSPORT
from .tornado_util import SERVER

HTML = u"""
<html>
    <body>
        <h1>test</h1>
    </body>
</html>
"""

class DocExtensionTest(TestCase):
    def setUp(self):
        SERVER.reset()

        # Create fake grab instance with fake response
        self.g = Grab(HTML, transport=GRAB_TRANSPORT)

    def test_extension_in_general(self):
        self.assertTrue(self.g.doc)

    def test_select_method(self):
        self.assertEqual('test', self.g.doc.select('//h1').text())
