#:coding=utf8:

from datetime import datetime
from unittest import TestCase

from beproud.utils.datastructures import *

class CachedPropObj(object):
    id = 0

    def spam(self):
        return datetime.now()

    @cached_property
    def cached_spam(self):
        return datetime.now()

    def eggs(self):
        self.__class__.id += 1
        return self.__class__.id

    @cached_property
    def cached_eggs(self):
        self.__class__.id += 1
        return self.__class__.id

class CachedPropertyTest(TestCase):

    def test_cached_property_get(self):
        obj = CachedPropObj()
        x = obj.cached_spam
        self.assertTrue(x)
        self.assertTrue(x is obj.cached_spam)

        y = obj.cached_eggs
        self.assertTrue(y)
        self.assertTrue(y is obj.cached_eggs)

    def test_cached_property_set(self):
        obj = CachedPropObj()
        obj.cached_spam = "spam"
        self.assertEqual(obj.cached_spam, "spam")

        self.assertTrue(obj.cached_eggs != "eggs")
        obj.cached_eggs = "eggs"
        self.assertEqual(obj.cached_eggs, "eggs")
