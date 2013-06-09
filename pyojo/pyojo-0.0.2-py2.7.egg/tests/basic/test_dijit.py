# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
from base import BasicTestCase

import pyojo.js as js
import pyojo.js.dojo as dojo
import pyojo.js.dijit as dijit

class TestDijit(BasicTestCase):
    def setUp(self):
        self.x = dijit.Dijit()
                
    def test_class(self):
        self.assertIsInstance(self.x, js.Code)
        self.assertIsInstance(self.x, dojo.Dojo)
        self.assertIsInstance(self.x, dijit.Dijit)
        assert str(type(self.x))=="<class 'pyojo.js.dijit.base.Dijit'>"
        
        print js.get_code(self.x)