import sys, os, unittest
from wm.sampledata.utils import getFileContent

import wm.sampledata.tests
from wm.sampledata import example

class FileUtilities(unittest.TestCase):


    def testPathWithModule(self):
        fc = getFileContent(wm.sampledata.tests, 'example', 'portlet.html')
        self.assertEqual(len(fc), 230)

    def testFileWithModule(self):
        fc = getFileContent(example, 'portlet.html')
        self.assertEqual(len(fc), 230)

    def testFileWithoutModule(self):
        pkgdir = os.path.dirname(wm.sampledata.tests.__file__)
        exdir = os.path.join(pkgdir, 'example')
        
        fc = getFileContent(None, exdir, 'portlet.html')
        self.assertEqual(len(fc), 230)


    def testNoFileWithModule(self):
        self.assertRaises(IOError, getFileContent, example, 'notexistent.html')
    
            

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(FileUtilities))
    return s
#
#def main():
#    unittest.TextTestRunner().run(test_suite())
#    
#if __name__=='__main__':
#    if len(sys.argv) > 1:
#        globals()[sys.argv[1]]()
#    else:
#        main()

