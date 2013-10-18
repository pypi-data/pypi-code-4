# XML Feeds OPML Document Parser (SAX)
# ======================================================================
import xml.sax
import logging

class OPMLFeedsContentHandler(xml.sax.ContentHandler):
    def __init__(self, xml_document):
        xml.sax.ContentHandler.__init__(self)
        # Build a nested dict that matches the XML data...
        self._feeds_d = { 'title': u'', 'feeds': [] }
        self._curr_tag = None

        # Execute parsing with "self" as ContentHandler...
        xml.sax.parseString(xml_document, self)

    def startElement(self, name, attrs):
        ## logging.debug("startElement '" + name + "'")
        self._curr_tag = name
        # Create another 'feeds' outline dict from attrs.
        if self._curr_tag == "outline":
            self._feeds_d['feeds'].append(dict(attrs))

    def endElement(self, name):
        ## logging.debug("endElement '" + name + "'")
        self._curr_tag = None

    def characters(self, content):
        ## logging.debug("characters '" + content + "'")
        # Read the 'title' from inside there.
        if self._curr_tag == "title":
            self._feeds_d['title'] = content

    def _get_feeds_dict(self):
        return self._feeds_d
    feeds_dict = property(_get_feeds_dict)

# Error Document Handler
class ErrorFeedsContentHandler(xml.sax.ContentHandler):
    def __init__(self, xml_document):
        xml.sax.ContentHandler.__init__(self)
        # Build a nested dict that matches the XML data...
        self._error_d = {}
        self._curr_tag = None

        # Execute parsing with "self" as ContentHandler...
        xml.sax.parseString(xml_document, self)

    def startElement(self, name, attrs):
        ## logging.debug("startElement '" + name + "'")
        self._curr_tag = name

    def endElement(self, name):
        ## logging.debug("endElement '" + name + "'")
        self._curr_tag = None

    def characters(self, content):
        ## logging.debug("characters '" + content + "'")
        # Read the 'title' from inside there.
        if self._curr_tag in [ 'result', 'errorCode', 'errorMessage' ]:
            self._error_d[self._curr_tag] = content

    def _get_error_dict(self):
        return self._error_d
    error_dict = property(_get_error_dict)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    from pprint import pprint

    xml_feeds = """<?xml version="1.0" encoding="UTF-8"?>
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
    xml_error = """<result>error</result>
<errorCode>oauth_consumer_key_absent</errorCode>
<errorMessage>Consumer key is absent</errorMessage>"""

    xml_doc = xml_feeds ## xml_error
    try:
        opml = OPMLFeedsContentHandler(xml_doc)
        pprint(opml.feeds_dict, indent=2)
    except xml.sax.SAXParseException:
        # Error Document is invalid XML; make it valid and parse it!
        logging.warn("Error Document is invalid XML; make it valid and parse it!")
        xml_error_doc = '\n'.join([ '<stream>', xml_doc, '</stream>' ])
        print xml_error_doc
        err = ErrorFeedsContentHandler(xml_error_doc)
        pprint(err.error_dict, indent=2)

