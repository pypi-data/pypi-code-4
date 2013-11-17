import unittest
from OFS.Application import Application

def makeConnection():
    import ZODB
    from ZODB.DemoStorage import DemoStorage

    s = DemoStorage()
    return ZODB.DB( s ).open()

class TestBase(unittest.TestCase):

    def setUp( self ):
        self.connection = makeConnection()
        r = self.connection.root()
        a = Application()
        r['Application'] = a
        self.root = a

    def test_get_adapter(self):
        self.root.get_browser
        self.root.getBrowser

if __name__ == '__main__':
    unittest.main()
