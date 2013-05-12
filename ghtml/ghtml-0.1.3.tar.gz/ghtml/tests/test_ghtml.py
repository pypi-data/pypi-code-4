import unittest

from ginsfsm.gobj import (
    GObj,
    )
from ginsfsm.ghtml import GHtml

import logging
logging.basicConfig(level=logging.DEBUG)


class Root(GObj):
    def __init__(self):
        super(Root, self).__init__({})
        self.start_up()

    def start_up(self):
        """ Setup area
        """


class Page1(GHtml):
    def __init__(self):
        super(Page1, self).__init__()

    def start_up(self):
        """ Setup area
        """
        settings = {
            'tag': 'div',
        }
        self.overwrite_parameters(1, **settings)


class Page2(GHtml):
    def __init__(self):
        super(Page2, self).__init__()

    def start_up(self):
        """ Setup area
        """


########################################################
#       Tests
########################################################
class TestGHtml(unittest.TestCase):
    def setUp(self):
        self.gobj_root = Root()
        settings = {
            'GObj.trace_mach': True,
            'GObj.logger': logging,
        }
        self.gobj_root.overwrite_parameters(-1, **settings)

    def test_page1(self):
        page = self.gobj_root.create_gobj(None, Page1, self.gobj_root)
        response = page.render()
        self.assertEqual(response, "<div></div>")

    def test_page2(self):
        page = self.gobj_root.create_gobj(
            None,
            Page2,
            self.gobj_root,
            tag='div')
        response = page.render()
        self.assertEqual(response, "<div></div>")

    def test_page3(self):
        page = self.gobj_root.create_gobj(
            None,
            Page2,
            self.gobj_root,
            template="<div></div>")
        response = page.render()
        self.assertEqual(response, "<div></div>")

    def test_page4(self):
        page = self.gobj_root.create_gobj(
            None,
            Page2,
            self.gobj_root,
            template="<div>${name}</div>")
        response = page.render(name='Hello')
        self.assertEqual(response, "<div>Hello</div>")
