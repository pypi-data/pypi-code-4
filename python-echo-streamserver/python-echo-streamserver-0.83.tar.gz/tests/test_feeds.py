import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('./')

from echo import feeds, StreamServerError

# Feed URL Samples (Account Dependent)
# ======================================================================
XML_HEADER='<?xml version="1.0" encoding="UTF-8"?>'

XML_FEEDS_RESULT = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
    <head>
        <title>Feeds for example.com</title>
    </head>
    <body>
        <outline text="http://example.com/feed/1" type="atom" xmlUrl="http://example.com/feed/1" refreshRate="300"/>
        <outline text="http://example.com/feed/2" type="atom" xmlUrl="http://example.com/feed/2" refreshRate="50"/>
    </body>
</opml>"""

# NOTE: Invalid error document is not XML w/o a root element "wrapper".
XML_ERROR_RESULT = """<result>error</result>
<errorCode>oauth_consumer_key_absent</errorCode>
<errorMessage>Consumer key is absent</errorMessage>"""

class Tests(unittest.TestCase):
    """Echo Feeds API Tests
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_feed_list(self):
        """ Return feeds list as a parsed dictionary. """
        try:
            r = feeds.list() # parsed=True by default
            self.assertIsInstance(r, dict)
            self.assertIn('feeds', r, "Feeds document has 'feeds'.")
            self.assertIsInstance(r['feeds'], list)
            self.assertIn('title', r, "Feeds document has 'title'.")
        except StreamServerError, e:
            raise

    def test_feed_list_xml(self):
        """ Return feeds list as OPML XML document, unparsed. """
        try:
            r = feeds.list(parsed=False)
            self.assertIsInstance(r, basestring)
            self.assertTrue(r.startswith(XML_HEADER), "Feeds document is not valid XML.")
        except StreamServerError, e:
            raise

