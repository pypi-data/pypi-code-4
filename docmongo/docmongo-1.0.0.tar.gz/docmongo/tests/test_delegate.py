import unittest


class TestDelegatePymongo(unittest.TestCase):
    def _makeOne(self):
        from docmongo.delegate import DelegatePymongo
        return DelegatePymongo

    def test_class_implements_IMongoDelegate(self):
        from zope.interface.verify import verifyClass
        from docmongo.interfaces import IMongoDelegate
        verifyClass(IMongoDelegate, self._makeOne())

    def test_instance_implements_IMongoDelegate(self):
        from zope.interface.verify import verifyObject
        from docmongo.interfaces import IMongoDelegate
        target = self._makeOne()
        verifyObject(IMongoDelegate, target('host', 'dbname', 'colname'))
