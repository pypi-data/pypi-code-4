# -*- coding: utf-8 -*-
import sys
import unittest
from urllib import quote_plus
from cStringIO import StringIO

try:
    import simplejson as json
except ImportError:
    import json

from Products.jsonserver.interfaces import IJsonRequest

from Products.jsonserver.jsonrpc import patch_HTTPRequest
from Products.jsonserver.jsonrpc import Response
patch_HTTPRequest()


class PublisherTests( unittest.TestCase ):

    def _getTargetClass(self):
        from ZPublisher.HTTPRequest import HTTPRequest
        return HTTPRequest

    def _makeOne(self, stdin=None, environ=None, clean=1):

        if stdin is None:
            stdin = StringIO('{ "method": "echo", "params": ["Hello JSON-RPC"], "id": 1}')

        if environ is None:
            environ = {}

        if 'SERVER_NAME' not in environ:
            environ['SERVER_NAME'] = 'http://localhost'

        if 'SERVER_PORT' not in environ:
            environ['SERVER_PORT'] = '8080'

        if 'REQUEST_METHOD' not in environ:
            environ['REQUEST_METHOD'] = 'POST'

        if 'CONTENT_TYPE' not in environ:
            environ['CONTENT_TYPE'] = 'application/json'

        class _FauxResponse(object):
            _auth = None
            _encode_unicode = None
            headers = {}

            def setHeader(self, key, value):
                self.headers[key] = value

            def setBody(self, body):
                self.body = body

            def setStatus(self, status):
                self.status = status

        response = _FauxResponse()
        req = self._getTargetClass()(stdin, environ, response, clean)
        req.processInputs()
        return req

    def test_marker(self):
        req = self._makeOne()
        self.failUnless(IJsonRequest.providedBy(req))

    def test_jsonid(self):
        req = self._makeOne()
        self.assertEqual(req.response._jsonID, 1)

    def test_body(self):
        req = self._makeOne()
        resp = req.response
        resp.setBody('Hello JSON-RPC')
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.body, '{"id": 1, "result": "Hello JSON-RPC"}')
        self.assertEqual(resp.headers,
                         {'content-type': 'application/json;charset=utf-8'})

    def test_get(self):
        req = self._makeOne(environ={'REQUEST_METHOD':'GET'})
        resp = req.response
        self.failIf(hasattr(resp, '_jsonID'))

    def test_wrongmimetype(self):
        req = self._makeOne(environ={'CONTENT_TYPE':'text/html'})
        self.failIf(hasattr(req.response, '_jsonID'))

    def test_alternatemimetype(self):
        req = self._makeOne(environ={'CONTENT_TYPE':'application/json-rpc'})
        self.assertEqual(req.response._jsonID, 1)

    def test_mimetypeencoding(self):
        encodings = ('iso-8859-1', 'utf-8')
        for enc in encodings:
            stdin = StringIO(
                u'{ "method": "methöd", "params": ["Hello JSON-RPC"], "id": 1}'.encode(enc))
            req = self._makeOne(stdin=stdin,
                environ={'CONTENT_TYPE': 'application/json-rpc; charset=%s' % enc})
            self.assertEqual(req.response._jsonID, 1)
            self.assertEqual(req.other['PATH_INFO'], '/meth\xc3\xb6d')

    def test_wrongmimetypeencoding(self):
        """ test if content-type and specified encoding don't fit """
        stdin = StringIO(
            u'{ "method": "methöd", "params": ["Hello JSON-RPC"], "id": 1}'.encode('iso-8859-1'))
        req = self._makeOne(stdin=stdin,
            environ={'CONTENT_TYPE': 'application/json-rpc; charset=utf-8'})
        self.assertEqual(req.other['PATH_INFO'], '/methd')

    def test_exception(self):
        # generate a response
        from ZPublisher.HTTPResponse import HTTPResponse
        real = HTTPResponse()
        resp = Response(real, 'jsonid1')

        # raise an exception
        try:
            1/0
        except ZeroDivisionError:
            info = sys.exc_info()
        resp.exception(info=info)

        # test the output according to
        # http://json-rpc.org/wd/JSON-RPC-1-1-WD-20060807.html#ErrorObject
        body = json.loads(resp.getBody())
        self.assertEqual(body['version'], '1.1')
        self.assertEqual(body['id'], 'jsonid1')
        self.assertEqual(body['error'],
                {u'code': 500,
                 u'message': u'ZeroDivisionError: integer division or modulo by zero',
                 u'name': u'JSONRPCError'})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublisherTests))
    return suite

