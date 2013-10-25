import unittest, sys, os
import pkg_resources

def runtest(testclass):
    suite = unittest.TestLoader().loadTestsFromTestCase(testclass)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
    if not testResult.wasSuccessful():
        sys.exit('[fose test wrapper] One or more tests failed!')

def runall():
    runtest(FoseTests)

class FoseTests(unittest.TestCase):

    def test_version(self):
        import fose
        pkgversion = pkg_resources.get_distribution("fose").version
        self.assertEqual(fose.version,pkgversion)

    def test_has_schemas(self):
        import fose
        schemaFilename = pkg_resources.resource_filename('fose','thread.xsd')
        self.assertTrue(os.path.isfile(schemaFilename))

    def test_uribuilder_single_publication_by_doi(self):
        from fose.protocol import UriBuilder
        expected = 'http://base.domain/doi/99.987/abc.1234'
        uriBuilder = UriBuilder('http://base.domain')
        self.assertEqual(expected, uriBuilder.forDoi('99.987/abc.1234'))

if __name__ == '__main__':
    unittest.main()
