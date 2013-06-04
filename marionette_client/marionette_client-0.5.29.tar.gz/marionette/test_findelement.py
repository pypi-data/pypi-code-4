# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from marionette_test import MarionetteTestCase
from marionette import HTMLElement
from errors import NoSuchElementException

class TestElements(MarionetteTestCase):
    def test_timeout(self):
        test_html = self.marionette.absolute_url("test.html")
        self.marionette.navigate(test_html)
        self.assertRaises(NoSuchElementException, self.marionette.find_element, "id", "newDiv")
        self.assertTrue(True, self.marionette.set_search_timeout(4000))
        self.marionette.navigate(test_html)
        self.assertEqual(HTMLElement, type(self.marionette.find_element("id", "newDiv")))
