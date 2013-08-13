from unittest import TestCase
from zope.interface.verify import verifyObject
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from collective.portlet.explore.browser.expand import DecorateStrategy
from collective.portlet.explore.tests.base import KSSTestCase

def yes(*args): return True
def no(*args): return False

class Dummy:
    pass

class MockRoot:
    def __init__(self, path=["", "root","child"]):
        self.path=path

    def getPhysicalPath(self):
        return self.path

    def getParentNode(self):
        return MockRoot(self.path[:-1])


class MockBrain:
    def __init__(self, path):
        self.path=path

    def getPath(self):
        return self.path


def CreateNode(path):
    return dict(item=MockBrain(path))


class TestDecorateStrategy(TestCase):
    def setUp(self):
        self.root=MockRoot()
        self.default=Dummy()
        self.strategy=DecorateStrategy(self.root, self.default)

    def testInterface(self):
        verifyObject(INavtreeStrategy, self.strategy)

    def testShowAllParentAlwaysTrue(self):
        self.default.showAllParents=False
        self.assertEqual(self.strategy.showAllParents, True)

    def testRootPathSetToOurRoot(self):
        self.default.rootPath="this is wrong"
        self.assertEqual(self.strategy.rootPath, "/root")

    def testNodeFilterDelegates(self):
        self.default.nodeFilter=yes 
        self.assertEqual(self.strategy.nodeFilter(CreateNode("/root/child/baby")), True)
        self.default.nodeFilter=no 
        self.assertEqual(self.strategy.nodeFilter(CreateNode("/root/child/baby")), False)

    def testNodeFilterRejectsOutsideRoot(self):
        self.default.nodeFilter=yes 
        self.assertEqual(self.strategy.nodeFilter(CreateNode("/other/child/baby")), False)

    def testNodeFilterAcceptsRoot(self):
        self.default.nodeFilter=yes 
        self.assertEqual(self.strategy.nodeFilter(CreateNode("/root/child")), True)

    def testNodeFilterAcceptsRootsChildren(self):
        self.default.nodeFilter=yes 
        self.assertEqual(self.strategy.nodeFilter(CreateNode("/root/child/baby")), True)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDecorateStrategy))
    return suite
