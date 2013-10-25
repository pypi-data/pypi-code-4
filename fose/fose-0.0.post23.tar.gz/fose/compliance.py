import unittest, sys
from fose.protocol import UriBuilder
import pkg_resources
from lxml import etree
import requests

### Test Data Section

TESTDOI = '99.789/fosetest.1'
TESTUID = 'a1B2c3D4'
REVIEWCONTENT = 'FOSE Compliance Test Review'


def runtest(testclass):
    suite = unittest.TestLoader().loadTestsFromTestCase(testclass)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
    if not testResult.wasSuccessful():
        sys.exit('[fose test wrapper] One or more tests failed!')

# These tests assume that the compliance test data have been installed
class ComplianceTests(unittest.TestCase):

    def setUp(self):
        self.uri = UriBuilder(self.rootUrl)

    def test_Get_review_thread_for_id(self):
		#use protocol url to GET response 
        url = self.uri.forDoi(TESTDOI)
        #actually get file
        response = requests.get(url, headers={'Accept':'text/xml'})
        response.raise_for_status()
		#test schema validation
        schemaFilename = pkg_resources.resource_filename('fose','thread.xsd')
        schema = etree.XMLSchema(file=schemaFilename)
        parser = etree.XMLParser(schema = schema)
        #THREAD = '<?xml version="1.0"?><thread xmlns="http://fose1.org/fose"/>'
        root = etree.fromstring(response.text, parser)
		#use core lib to read this as a model object
		#for each review in thread, test if it is a review by user 'a1B2c3D4'
        # with content 'FOSE Compliance Test Review' 

    def test_Get_user_profile_for_uid(self):
		#use protocol url to GET response 
        url = self.uri.forUser(TESTUID)
        #actually get file
        response = requests.get(url, headers={'Accept':'text/xml'})
        response.raise_for_status()
		#test schema validation
        schemaFilename = pkg_resources.resource_filename('fose','user.xsd')
        schema = etree.XMLSchema(file=schemaFilename)
        parser = etree.XMLParser(schema = schema)
        #THREAD = '<?xml version="1.0"?><thread xmlns="http://fose1.org/fose"/>'
        root = etree.fromstring(response.text, parser)
		#use core lib to read this as a model object
		#for each review by user, test if it is a review 
        # for doi '99.789/fosetest.1' with content 'FOSE Compliance Test Review' 

def run(targetUrl):
    ComplianceTests.rootUrl = targetUrl
    runtest(ComplianceTests)

if __name__ == '__main__':
    unittest.main()
