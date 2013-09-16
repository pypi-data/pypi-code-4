# Copyright (c) 2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

from cStringIO import StringIO

from nose.tools import assert_equal
from flea import TestAgent

from fresco.util.http import parse_querystring, parse_post
from fresco import FrescoApp, Response, GET, POST

from . import form_data


class TestParseQueryString(object):

    def p(self, value):
        return list(parse_querystring(value))

    def test_empty(self):
        assert_equal(self.p(''), [])

    def test_simple_key_value(self):
        assert_equal(self.p('a=b'), [('a', 'b')])

    def test_key_with_space(self):
        assert_equal(self.p('a+b=c'), [('a b', 'c')])

    def test_value_with_space(self):
        assert_equal(self.p('a=b+c'), [('a', 'b c')])

    def test_double_equals(self):
        assert_equal(self.p('a==b'), [('a', '=b')])

    def test_escaped_chars(self):
        assert_equal(self.p('%20==c%3D'), [(' ', '=c=')])


class TestParseMultipart(object):

    def test_multipart(self):
        for data in form_data.multipart_samples:
            io = StringIO(data['data'])
            io.seek(0)
            environ = {
                'CONTENT_LENGTH': data['content_length'],
                'CONTENT_TYPE': data['content_type'],
            }
            parsed = sorted(list(parse_post(environ, io, 'UTF-8')))

            assert_equal(
                [name for name, value in parsed],
                ["empty-text-input", "file-upload", "text-input-ascii",
                "text-input-unicode"]
            )

            assert_equal(parsed[0], ("empty-text-input", ""))
            assert_equal(parsed[2], ("text-input-ascii", "abcdef"))
            assert_equal(parsed[3], ("text-input-unicode",
                                    "\xce\xb1\xce\xb2\xce\xb3\xce\xb4"\
                                    .decode("utf8")))

            fieldname, fileupload = parsed[1]
            assert_equal(fieldname, "file-upload")
            assert_equal(fileupload.filename, "test.data")
            assert_equal(fileupload.headers['content-type'],
                        "application/octet-stream")
            assert_equal(fileupload.file.read(), form_data.FILE_UPLOAD_DATA)

    def test_fileupload_too_big(self):
        """\
        Verify that multipart/form-data encoded POST data raises an exception
        if the total data size exceeds request.MAX_SIZE bytes
        """

        def view(request):
            request.MAX_MULTIPART_SIZE = 500
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post_multipart(
            files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)],
            check_status=False
        )
        assert_equal(r.response.status, "413 Request Entity Too Large")

        r = TestAgent(app).post_multipart(
            files=[('f1', 'filename.txt', 'text/plain', 'x' * 400)],
            data={'f2': 'x' * 101},
            check_status=False
        )
        assert_equal(r.response.status, "413 Request Entity Too Large")

    def test_fileupload_with_invalid_content_length(self):

        def view(request):
            request.MAX_MULTIPART_SIZE = 500
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post_multipart(
            files=[('f1', 'filename.txt', 'text/plain', 'x' * 1000)],
            CONTENT_LENGTH="499",
            check_status=False
        )
        assert_equal(r.response.status, "400 Bad Request")

    def test_multipart_field_too_big(self):
        """
        Verify that multipart/form-data encoded POST data raises an exception
        if it contains a single field exceeding request.MAX_SIZE bytes
        """
        def view(request):
            request.MAX_MULTIPART_SIZE = 500
            request.MAX_SIZE = 100
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post_multipart(data=[('f1', 'x' * 200)],
                                        check_status=False)
        assert_equal(r.response.status, "413 Request Entity Too Large")


class TestParseFormEncodedData(object):

    def test_formencoded_data_too_big(self):
        """
        Verify that application/x-www-form-urlencoded POST data raises an
        exception if it exceeds request.MAX_SIZE bytes
        """
        def view(request):
            request.MAX_SIZE = 100
            request.get('f1')
            return Response(['ok'])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post(data=[('f1', 'x' * 200)], check_status=False)
        assert_equal(r.response.status, "413 Request Entity Too Large")

    def test_non_utf8_data_posted(self):

        def view(request):
            request.charset = 'latin1'
            x = request.form['char']
            return Response([x.encode('utf8')])
        app = FrescoApp()
        app.route('/', POST, view)

        r = TestAgent(app).post(data={'char': u'\u00a3'.encode('latin1')},
                                check_status=False)
        assert_equal(r.response.body.decode('utf8'), u"\u00a3")

    def test_non_utf8_data_getted(self):

        def view(request):
            request.charset = 'latin1'
            x = request.form['char']
            return Response([x.encode('utf8')])
        app = FrescoApp()
        app.route('/', GET, view)

        r = TestAgent(app).get(data={'char': u'\u00a3'.encode('latin1')},
                            check_status=False)
        assert_equal(r.response.body.decode('utf8'), u"\u00a3")
