# -*- coding: utf-8 -*-

import unittest
from .plugin import *


class TestBookmark(unittest.TestCase):

    def test_title(self):
        self.assertEquals(Bookmark({"description": "desc"}).title, "desc")
        self.assertEquals(Bookmark({}).title, None)

    def test_description(self):
        self.assertEquals(Bookmark({"extended": "ext"}).description, "ext")
        self.assertEquals(Bookmark({}).title, None)

    def test_href(self):
        self.assertEquals(Bookmark({"href": "url"}).href, "url")
        self.assertEquals(Bookmark({}).title, None)

    def test_tags(self):
        self.assertEquals(
            Bookmark({"tag": "tag1 tag2"}).tags, set(["tag1", "tag2"]))
        self.assertEquals(Bookmark({}).tags, set())


class TestDelicious(unittest.TestCase):

    def test_fetch_delicious(self):
        pass

    def test_setup_delicious(self):
        pass

    def test_replace_delicious_tags(self):
        pass
