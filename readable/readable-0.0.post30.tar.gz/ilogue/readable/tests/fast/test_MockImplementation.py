import unittest
from zope.interface import Interface
from zope.component import getGlobalSiteManager


class MockImplementationTest(unittest.TestCase):

    def setUp(self):
        self.gsm = getGlobalSiteManager()

    def test_MockImplementation(self):
        from ilogue.readable.MockImplementation import mockImplementation
        class ISomething(Interface):
            pass
        mi = mockImplementation(ISomething)
        self.gsm.registerUtility(mi)
        returned = self.gsm.getUtility(ISomething)
        mi.doSomething()
        self.assertIs(returned,mi)


if __name__ == '__main__':
    unittest.main()


