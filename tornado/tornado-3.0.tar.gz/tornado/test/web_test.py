from __future__ import absolute_import, division, print_function, with_statement
from tornado import gen
from tornado.escape import json_decode, utf8, to_unicode, recursive_unicode, native_str, to_basestring
from tornado.iostream import IOStream
from tornado.log import app_log, gen_log
from tornado.simple_httpclient import SimpleAsyncHTTPClient
from tornado.template import DictLoader
from tornado.testing import AsyncHTTPTestCase, ExpectLog
from tornado.test.util import unittest
from tornado.util import u, bytes_type, ObjectDict, unicode_type
from tornado.web import RequestHandler, authenticated, Application, asynchronous, url, HTTPError, StaticFileHandler, _create_signature, create_signed_value, ErrorHandler

import binascii
import datetime
import logging
import os
import re
import socket
import sys

wsgi_safe_tests = []


def wsgi_safe(cls):
    wsgi_safe_tests.append(cls)
    return cls


class WebTestCase(AsyncHTTPTestCase):
    """Base class for web tests that also supports WSGI mode.

    Override get_handlers and get_app_kwargs instead of get_app.
    Append to wsgi_safe to have it run in wsgi_test as well.
    """
    def get_app(self):
        self.app = Application(self.get_handlers(), **self.get_app_kwargs())
        return self.app

    def get_handlers(self):
        raise NotImplementedError()

    def get_app_kwargs(self):
        return {}


class SimpleHandlerTestCase(WebTestCase):
    """Simplified base class for tests that work with a single handler class.

    To use, define a nested class named ``Handler``.
    """
    def get_handlers(self):
        return [('/', self.Handler)]


class CookieTestRequestHandler(RequestHandler):
    # stub out enough methods to make the secure_cookie functions work
    def __init__(self):
        # don't call super.__init__
        self._cookies = {}
        self.application = ObjectDict(settings=dict(cookie_secret='0123456789'))

    def get_cookie(self, name):
        return self._cookies.get(name)

    def set_cookie(self, name, value, expires_days=None):
        self._cookies[name] = value


class SecureCookieTest(unittest.TestCase):
    def test_round_trip(self):
        handler = CookieTestRequestHandler()
        handler.set_secure_cookie('foo', b'bar')
        self.assertEqual(handler.get_secure_cookie('foo'), b'bar')

    def test_cookie_tampering_future_timestamp(self):
        handler = CookieTestRequestHandler()
        # this string base64-encodes to '12345678'
        handler.set_secure_cookie('foo', binascii.a2b_hex(b'd76df8e7aefc'))
        cookie = handler._cookies['foo']
        match = re.match(br'12345678\|([0-9]+)\|([0-9a-f]+)', cookie)
        self.assertTrue(match)
        timestamp = match.group(1)
        sig = match.group(2)
        self.assertEqual(
            _create_signature(handler.application.settings["cookie_secret"],
                              'foo', '12345678', timestamp),
            sig)
        # shifting digits from payload to timestamp doesn't alter signature
        # (this is not desirable behavior, just confirming that that's how it
        # works)
        self.assertEqual(
            _create_signature(handler.application.settings["cookie_secret"],
                              'foo', '1234', b'5678' + timestamp),
            sig)
        # tamper with the cookie
        handler._cookies['foo'] = utf8('1234|5678%s|%s' % (
            to_basestring(timestamp), to_basestring(sig)))
        # it gets rejected
        with ExpectLog(gen_log, "Cookie timestamp in future"):
            self.assertTrue(handler.get_secure_cookie('foo') is None)

    def test_arbitrary_bytes(self):
        # Secure cookies accept arbitrary data (which is base64 encoded).
        # Note that normal cookies accept only a subset of ascii.
        handler = CookieTestRequestHandler()
        handler.set_secure_cookie('foo', b'\xe9')
        self.assertEqual(handler.get_secure_cookie('foo'), b'\xe9')


class CookieTest(WebTestCase):
    def get_handlers(self):
        class SetCookieHandler(RequestHandler):
            def get(self):
                # Try setting cookies with different argument types
                # to ensure that everything gets encoded correctly
                self.set_cookie("str", "asdf")
                self.set_cookie("unicode", u("qwer"))
                self.set_cookie("bytes", b"zxcv")

        class GetCookieHandler(RequestHandler):
            def get(self):
                self.write(self.get_cookie("foo", "default"))

        class SetCookieDomainHandler(RequestHandler):
            def get(self):
                # unicode domain and path arguments shouldn't break things
                # either (see bug #285)
                self.set_cookie("unicode_args", "blah", domain=u("foo.com"),
                                path=u("/foo"))

        class SetCookieSpecialCharHandler(RequestHandler):
            def get(self):
                self.set_cookie("equals", "a=b")
                self.set_cookie("semicolon", "a;b")
                self.set_cookie("quote", 'a"b')

        class SetCookieOverwriteHandler(RequestHandler):
            def get(self):
                self.set_cookie("a", "b", domain="example.com")
                self.set_cookie("c", "d", domain="example.com")
                # A second call with the same name clobbers the first.
                # Attributes from the first call are not carried over.
                self.set_cookie("a", "e")

        return [("/set", SetCookieHandler),
                ("/get", GetCookieHandler),
                ("/set_domain", SetCookieDomainHandler),
                ("/special_char", SetCookieSpecialCharHandler),
                ("/set_overwrite", SetCookieOverwriteHandler),
                ]

    def test_set_cookie(self):
        response = self.fetch("/set")
        self.assertEqual(sorted(response.headers.get_list("Set-Cookie")),
                         ["bytes=zxcv; Path=/",
                          "str=asdf; Path=/",
                          "unicode=qwer; Path=/",
                          ])

    def test_get_cookie(self):
        response = self.fetch("/get", headers={"Cookie": "foo=bar"})
        self.assertEqual(response.body, b"bar")

        response = self.fetch("/get", headers={"Cookie": 'foo="bar"'})
        self.assertEqual(response.body, b"bar")

        response = self.fetch("/get", headers={"Cookie": "/=exception;"})
        self.assertEqual(response.body, b"default")

    def test_set_cookie_domain(self):
        response = self.fetch("/set_domain")
        self.assertEqual(response.headers.get_list("Set-Cookie"),
                         ["unicode_args=blah; Domain=foo.com; Path=/foo"])

    def test_cookie_special_char(self):
        response = self.fetch("/special_char")
        headers = sorted(response.headers.get_list("Set-Cookie"))
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers[0], 'equals="a=b"; Path=/')
        self.assertEqual(headers[1], 'quote="a\\"b"; Path=/')
        # python 2.7 octal-escapes the semicolon; older versions leave it alone
        self.assertTrue(headers[2] in ('semicolon="a;b"; Path=/',
                                       'semicolon="a\\073b"; Path=/'),
                        headers[2])

        data = [('foo=a=b', 'a=b'),
                ('foo="a=b"', 'a=b'),
                ('foo="a;b"', 'a;b'),
                #('foo=a\\073b', 'a;b'),  # even encoded, ";" is a delimiter
                ('foo="a\\073b"', 'a;b'),
                ('foo="a\\"b"', 'a"b'),
                ]
        for header, expected in data:
            logging.debug("trying %r", header)
            response = self.fetch("/get", headers={"Cookie": header})
            self.assertEqual(response.body, utf8(expected))

    def test_set_cookie_overwrite(self):
        response = self.fetch("/set_overwrite")
        headers = response.headers.get_list("Set-Cookie")
        self.assertEqual(sorted(headers),
                         ["a=e; Path=/", "c=d; Domain=example.com; Path=/"])


class AuthRedirectRequestHandler(RequestHandler):
    def initialize(self, login_url):
        self.login_url = login_url

    def get_login_url(self):
        return self.login_url

    @authenticated
    def get(self):
        # we'll never actually get here because the test doesn't follow redirects
        self.send_error(500)


class AuthRedirectTest(WebTestCase):
    def get_handlers(self):
        return [('/relative', AuthRedirectRequestHandler,
                 dict(login_url='/login')),
                ('/absolute', AuthRedirectRequestHandler,
                 dict(login_url='http://example.com/login'))]

    def test_relative_auth_redirect(self):
        self.http_client.fetch(self.get_url('/relative'), self.stop,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers['Location'], '/login?next=%2Frelative')

    def test_absolute_auth_redirect(self):
        self.http_client.fetch(self.get_url('/absolute'), self.stop,
                               follow_redirects=False)
        response = self.wait()
        self.assertEqual(response.code, 302)
        self.assertTrue(re.match(
            'http://example.com/login\?next=http%3A%2F%2Flocalhost%3A[0-9]+%2Fabsolute',
            response.headers['Location']), response.headers['Location'])


class ConnectionCloseHandler(RequestHandler):
    def initialize(self, test):
        self.test = test

    @asynchronous
    def get(self):
        self.test.on_handler_waiting()

    def on_connection_close(self):
        self.test.on_connection_close()


class ConnectionCloseTest(WebTestCase):
    def get_handlers(self):
        return [('/', ConnectionCloseHandler, dict(test=self))]

    def test_connection_close(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.connect(("localhost", self.get_http_port()))
        self.stream = IOStream(s, io_loop=self.io_loop)
        self.stream.write(b"GET / HTTP/1.0\r\n\r\n")
        self.wait()

    def on_handler_waiting(self):
        logging.debug('handler waiting')
        self.stream.close()

    def on_connection_close(self):
        logging.debug('connection closed')
        self.stop()


class EchoHandler(RequestHandler):
    def get(self, *path_args):
        # Type checks: web.py interfaces convert argument values to
        # unicode strings (by default, but see also decode_argument).
        # In httpserver.py (i.e. self.request.arguments), they're left
        # as bytes.  Keys are always native strings.
        for key in self.request.arguments:
            if type(key) != str:
                raise Exception("incorrect type for key: %r" % type(key))
            for value in self.request.arguments[key]:
                if type(value) != bytes_type:
                    raise Exception("incorrect type for value: %r" %
                                    type(value))
            for value in self.get_arguments(key):
                if type(value) != unicode_type:
                    raise Exception("incorrect type for value: %r" %
                                    type(value))
        for arg in path_args:
            if type(arg) != unicode_type:
                raise Exception("incorrect type for path arg: %r" % type(arg))
        self.write(dict(path=self.request.path,
                        path_args=path_args,
                        args=recursive_unicode(self.request.arguments)))


class RequestEncodingTest(WebTestCase):
    def get_handlers(self):
        return [("/group/(.*)", EchoHandler),
                ("/slashes/([^/]*)/([^/]*)", EchoHandler),
                ]

    def fetch_json(self, path):
        return json_decode(self.fetch(path).body)

    def test_group_question_mark(self):
        # Ensure that url-encoded question marks are handled properly
        self.assertEqual(self.fetch_json('/group/%3F'),
                         dict(path='/group/%3F', path_args=['?'], args={}))
        self.assertEqual(self.fetch_json('/group/%3F?%3F=%3F'),
                         dict(path='/group/%3F', path_args=['?'], args={'?': ['?']}))

    def test_group_encoding(self):
        # Path components and query arguments should be decoded the same way
        self.assertEqual(self.fetch_json('/group/%C3%A9?arg=%C3%A9'),
                         {u("path"): u("/group/%C3%A9"),
                          u("path_args"): [u("\u00e9")],
                          u("args"): {u("arg"): [u("\u00e9")]}})

    def test_slashes(self):
        # Slashes may be escaped to appear as a single "directory" in the path,
        # but they are then unescaped when passed to the get() method.
        self.assertEqual(self.fetch_json('/slashes/foo/bar'),
                         dict(path="/slashes/foo/bar",
                              path_args=["foo", "bar"],
                              args={}))
        self.assertEqual(self.fetch_json('/slashes/a%2Fb/c%2Fd'),
                         dict(path="/slashes/a%2Fb/c%2Fd",
                              path_args=["a/b", "c/d"],
                              args={}))


class TypeCheckHandler(RequestHandler):
    def prepare(self):
        self.errors = {}

        self.check_type('status', self.get_status(), int)

        # get_argument is an exception from the general rule of using
        # type str for non-body data mainly for historical reasons.
        self.check_type('argument', self.get_argument('foo'), unicode_type)
        self.check_type('cookie_key', list(self.cookies.keys())[0], str)
        self.check_type('cookie_value', list(self.cookies.values())[0].value, str)

        # Secure cookies return bytes because they can contain arbitrary
        # data, but regular cookies are native strings.
        if list(self.cookies.keys()) != ['asdf']:
            raise Exception("unexpected values for cookie keys: %r" %
                            self.cookies.keys())
        self.check_type('get_secure_cookie', self.get_secure_cookie('asdf'), bytes_type)
        self.check_type('get_cookie', self.get_cookie('asdf'), str)

        self.check_type('xsrf_token', self.xsrf_token, bytes_type)
        self.check_type('xsrf_form_html', self.xsrf_form_html(), str)

        self.check_type('reverse_url', self.reverse_url('typecheck', 'foo'), str)

        self.check_type('request_summary', self._request_summary(), str)

    def get(self, path_component):
        # path_component uses type unicode instead of str for consistency
        # with get_argument()
        self.check_type('path_component', path_component, unicode_type)
        self.write(self.errors)

    def post(self, path_component):
        self.check_type('path_component', path_component, unicode_type)
        self.write(self.errors)

    def check_type(self, name, obj, expected_type):
        actual_type = type(obj)
        if expected_type != actual_type:
            self.errors[name] = "expected %s, got %s" % (expected_type,
                                                         actual_type)


class DecodeArgHandler(RequestHandler):
    def decode_argument(self, value, name=None):
        if type(value) != bytes_type:
            raise Exception("unexpected type for value: %r" % type(value))
        # use self.request.arguments directly to avoid recursion
        if 'encoding' in self.request.arguments:
            return value.decode(to_unicode(self.request.arguments['encoding'][0]))
        else:
            return value

    def get(self, arg):
        def describe(s):
            if type(s) == bytes_type:
                return ["bytes", native_str(binascii.b2a_hex(s))]
            elif type(s) == unicode_type:
                return ["unicode", s]
            raise Exception("unknown type")
        self.write({'path': describe(arg),
                    'query': describe(self.get_argument("foo")),
                    })


class LinkifyHandler(RequestHandler):
    def get(self):
        self.render("linkify.html", message="http://example.com")


class UIModuleResourceHandler(RequestHandler):
    def get(self):
        self.render("page.html", entries=[1, 2])


class OptionalPathHandler(RequestHandler):
    def get(self, path):
        self.write({"path": path})


class FlowControlHandler(RequestHandler):
    # These writes are too small to demonstrate real flow control,
    # but at least it shows that the callbacks get run.
    @asynchronous
    def get(self):
        self.write("1")
        self.flush(callback=self.step2)

    def step2(self):
        self.write("2")
        self.flush(callback=self.step3)

    def step3(self):
        self.write("3")
        self.finish()


class MultiHeaderHandler(RequestHandler):
    def get(self):
        self.set_header("x-overwrite", "1")
        self.set_header("X-Overwrite", 2)
        self.add_header("x-multi", 3)
        self.add_header("X-Multi", "4")


class RedirectHandler(RequestHandler):
    def get(self):
        if self.get_argument('permanent', None) is not None:
            self.redirect('/', permanent=int(self.get_argument('permanent')))
        elif self.get_argument('status', None) is not None:
            self.redirect('/', status=int(self.get_argument('status')))
        else:
            raise Exception("didn't get permanent or status arguments")


class EmptyFlushCallbackHandler(RequestHandler):
    @gen.engine
    @asynchronous
    def get(self):
        # Ensure that the flush callback is run whether or not there
        # was any output.
        yield gen.Task(self.flush)  # "empty" flush, but writes headers
        yield gen.Task(self.flush)  # empty flush
        self.write("o")
        yield gen.Task(self.flush)  # flushes the "o"
        yield gen.Task(self.flush)  # empty flush
        self.finish("k")


class HeaderInjectionHandler(RequestHandler):
    def get(self):
        try:
            self.set_header("X-Foo", "foo\r\nX-Bar: baz")
            raise Exception("Didn't get expected exception")
        except ValueError as e:
            if "Unsafe header value" in str(e):
                self.finish(b"ok")
            else:
                raise


class GetArgumentHandler(RequestHandler):
    def get(self):
        self.write(self.get_argument("foo", "default"))


# This test is shared with wsgi_test.py
@wsgi_safe
class WSGISafeWebTest(WebTestCase):
    COOKIE_SECRET = "WebTest.COOKIE_SECRET"

    def get_app_kwargs(self):
        loader = DictLoader({
            "linkify.html": "{% module linkify(message) %}",
            "page.html": """\
<html><head></head><body>
{% for e in entries %}
{% module Template("entry.html", entry=e) %}
{% end %}
</body></html>""",
            "entry.html": """\
{{ set_resources(embedded_css=".entry { margin-bottom: 1em; }", embedded_javascript="js_embed()", css_files=["/base.css", "/foo.css"], javascript_files="/common.js", html_head="<meta>", html_body='<script src="/analytics.js"/>') }}
<div class="entry">...</div>""",
        })
        return dict(template_loader=loader,
                    autoescape="xhtml_escape",
                    cookie_secret=self.COOKIE_SECRET)

    def get_handlers(self):
        urls = [
            url("/typecheck/(.*)", TypeCheckHandler, name='typecheck'),
            url("/decode_arg/(.*)", DecodeArgHandler, name='decode_arg'),
            url("/decode_arg_kw/(?P<arg>.*)", DecodeArgHandler),
            url("/linkify", LinkifyHandler),
            url("/uimodule_resources", UIModuleResourceHandler),
            url("/optional_path/(.+)?", OptionalPathHandler),
            url("/multi_header", MultiHeaderHandler),
            url("/redirect", RedirectHandler),
            url("/header_injection", HeaderInjectionHandler),
            url("/get_argument", GetArgumentHandler),
        ]
        return urls

    def fetch_json(self, *args, **kwargs):
        response = self.fetch(*args, **kwargs)
        response.rethrow()
        return json_decode(response.body)

    def test_types(self):
        cookie_value = to_unicode(create_signed_value(self.COOKIE_SECRET,
                                                      "asdf", "qwer"))
        response = self.fetch("/typecheck/asdf?foo=bar",
                              headers={"Cookie": "asdf=" + cookie_value})
        data = json_decode(response.body)
        self.assertEqual(data, {})

        response = self.fetch("/typecheck/asdf?foo=bar", method="POST",
                              headers={"Cookie": "asdf=" + cookie_value},
                              body="foo=bar")

    def test_decode_argument(self):
        # These urls all decode to the same thing
        urls = ["/decode_arg/%C3%A9?foo=%C3%A9&encoding=utf-8",
                "/decode_arg/%E9?foo=%E9&encoding=latin1",
                "/decode_arg_kw/%E9?foo=%E9&encoding=latin1",
                ]
        for url in urls:
            response = self.fetch(url)
            response.rethrow()
            data = json_decode(response.body)
            self.assertEqual(data, {u('path'): [u('unicode'), u('\u00e9')],
                                    u('query'): [u('unicode'), u('\u00e9')],
                                    })

        response = self.fetch("/decode_arg/%C3%A9?foo=%C3%A9")
        response.rethrow()
        data = json_decode(response.body)
        self.assertEqual(data, {u('path'): [u('bytes'), u('c3a9')],
                                u('query'): [u('bytes'), u('c3a9')],
                                })

    def test_reverse_url(self):
        self.assertEqual(self.app.reverse_url('decode_arg', 'foo'),
                         '/decode_arg/foo')
        self.assertEqual(self.app.reverse_url('decode_arg', 42),
                         '/decode_arg/42')
        self.assertEqual(self.app.reverse_url('decode_arg', b'\xe9'),
                         '/decode_arg/%E9')
        self.assertEqual(self.app.reverse_url('decode_arg', u('\u00e9')),
                         '/decode_arg/%C3%A9')

    def test_uimodule_unescaped(self):
        response = self.fetch("/linkify")
        self.assertEqual(response.body,
                         b"<a href=\"http://example.com\">http://example.com</a>")

    def test_uimodule_resources(self):
        response = self.fetch("/uimodule_resources")
        self.assertEqual(response.body, b"""\
<html><head><link href="/base.css" type="text/css" rel="stylesheet"/><link href="/foo.css" type="text/css" rel="stylesheet"/>
<style type="text/css">
.entry { margin-bottom: 1em; }
</style>
<meta>
</head><body>


<div class="entry">...</div>


<div class="entry">...</div>

<script src="/common.js" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[
js_embed()
//]]>
</script>
<script src="/analytics.js"/>
</body></html>""")

    def test_optional_path(self):
        self.assertEqual(self.fetch_json("/optional_path/foo"),
                         {u("path"): u("foo")})
        self.assertEqual(self.fetch_json("/optional_path/"),
                         {u("path"): None})

    def test_multi_header(self):
        response = self.fetch("/multi_header")
        self.assertEqual(response.headers["x-overwrite"], "2")
        self.assertEqual(response.headers.get_list("x-multi"), ["3", "4"])

    def test_redirect(self):
        response = self.fetch("/redirect?permanent=1", follow_redirects=False)
        self.assertEqual(response.code, 301)
        response = self.fetch("/redirect?permanent=0", follow_redirects=False)
        self.assertEqual(response.code, 302)
        response = self.fetch("/redirect?status=307", follow_redirects=False)
        self.assertEqual(response.code, 307)

    def test_header_injection(self):
        response = self.fetch("/header_injection")
        self.assertEqual(response.body, b"ok")

    def test_get_argument(self):
        response = self.fetch("/get_argument?foo=bar")
        self.assertEqual(response.body, b"bar")
        response = self.fetch("/get_argument?foo=")
        self.assertEqual(response.body, b"")
        response = self.fetch("/get_argument")
        self.assertEqual(response.body, b"default")

    def test_no_gzip(self):
        response = self.fetch('/get_argument')
        self.assertNotIn('Accept-Encoding', response.headers.get('Vary', ''))
        self.assertNotIn('gzip', response.headers.get('Content-Encoding', ''))


class NonWSGIWebTests(WebTestCase):
    def get_handlers(self):
        return [("/flow_control", FlowControlHandler),
                ("/empty_flush", EmptyFlushCallbackHandler),
                ]

    def test_flow_control(self):
        self.assertEqual(self.fetch("/flow_control").body, b"123")

    def test_empty_flush(self):
        response = self.fetch("/empty_flush")
        self.assertEqual(response.body, b"ok")


@wsgi_safe
class ErrorResponseTest(WebTestCase):
    def get_handlers(self):
        class DefaultHandler(RequestHandler):
            def get(self):
                if self.get_argument("status", None):
                    raise HTTPError(int(self.get_argument("status")))
                1 / 0

        class WriteErrorHandler(RequestHandler):
            def get(self):
                if self.get_argument("status", None):
                    self.send_error(int(self.get_argument("status")))
                else:
                    1 / 0

            def write_error(self, status_code, **kwargs):
                self.set_header("Content-Type", "text/plain")
                if "exc_info" in kwargs:
                    self.write("Exception: %s" % kwargs["exc_info"][0].__name__)
                else:
                    self.write("Status: %d" % status_code)

        class GetErrorHtmlHandler(RequestHandler):
            def get(self):
                if self.get_argument("status", None):
                    self.send_error(int(self.get_argument("status")))
                else:
                    1 / 0

            def get_error_html(self, status_code, **kwargs):
                self.set_header("Content-Type", "text/plain")
                if "exception" in kwargs:
                    self.write("Exception: %s" % sys.exc_info()[0].__name__)
                else:
                    self.write("Status: %d" % status_code)

        class FailedWriteErrorHandler(RequestHandler):
            def get(self):
                1 / 0

            def write_error(self, status_code, **kwargs):
                raise Exception("exception in write_error")

        return [url("/default", DefaultHandler),
                url("/write_error", WriteErrorHandler),
                url("/get_error_html", GetErrorHtmlHandler),
                url("/failed_write_error", FailedWriteErrorHandler),
                ]

    def test_default(self):
        with ExpectLog(app_log, "Uncaught exception"):
            response = self.fetch("/default")
            self.assertEqual(response.code, 500)
            self.assertTrue(b"500: Internal Server Error" in response.body)

            response = self.fetch("/default?status=503")
            self.assertEqual(response.code, 503)
            self.assertTrue(b"503: Service Unavailable" in response.body)

    def test_write_error(self):
        with ExpectLog(app_log, "Uncaught exception"):
            response = self.fetch("/write_error")
            self.assertEqual(response.code, 500)
            self.assertEqual(b"Exception: ZeroDivisionError", response.body)

            response = self.fetch("/write_error?status=503")
            self.assertEqual(response.code, 503)
            self.assertEqual(b"Status: 503", response.body)

    def test_get_error_html(self):
        with ExpectLog(app_log, "Uncaught exception"):
            response = self.fetch("/get_error_html")
            self.assertEqual(response.code, 500)
            self.assertEqual(b"Exception: ZeroDivisionError", response.body)

            response = self.fetch("/get_error_html?status=503")
            self.assertEqual(response.code, 503)
            self.assertEqual(b"Status: 503", response.body)

    def test_failed_write_error(self):
        with ExpectLog(app_log, "Uncaught exception"):
            response = self.fetch("/failed_write_error")
            self.assertEqual(response.code, 500)
            self.assertEqual(b"", response.body)


@wsgi_safe
class StaticFileTest(WebTestCase):
    def get_handlers(self):
        class StaticUrlHandler(RequestHandler):
            def get(self, path):
                self.write(self.static_url(path))

        class AbsoluteStaticUrlHandler(RequestHandler):
            include_host = True

            def get(self, path):
                self.write(self.static_url(path))

        class OverrideStaticUrlHandler(RequestHandler):
            def get(self, path):
                do_include = bool(self.get_argument("include_host"))
                self.include_host = not do_include

                regular_url = self.static_url(path)
                override_url = self.static_url(path, include_host=do_include)
                if override_url == regular_url:
                    return self.write(str(False))

                protocol = self.request.protocol + "://"
                protocol_length = len(protocol)
                check_regular = regular_url.find(protocol, 0, protocol_length)
                check_override = override_url.find(protocol, 0, protocol_length)

                if do_include:
                    result = (check_override == 0 and check_regular == -1)
                else:
                    result = (check_override == -1 and check_regular == 0)
                self.write(str(result))

        return [('/static_url/(.*)', StaticUrlHandler),
                ('/abs_static_url/(.*)', AbsoluteStaticUrlHandler),
                ('/override_static_url/(.*)', OverrideStaticUrlHandler)]

    def get_app_kwargs(self):
        return dict(static_path=os.path.join(os.path.dirname(__file__),
                                             'static'))

    def test_static_files(self):
        response = self.fetch('/robots.txt')
        self.assertTrue(b"Disallow: /" in response.body)

        response = self.fetch('/static/robots.txt')
        self.assertTrue(b"Disallow: /" in response.body)

    def test_static_url(self):
        response = self.fetch("/static_url/robots.txt")
        self.assertEqual(response.body, b"/static/robots.txt?v=f71d2")

    def test_absolute_static_url(self):
        response = self.fetch("/abs_static_url/robots.txt")
        self.assertEqual(response.body,
                         utf8(self.get_url("/") + "static/robots.txt?v=f71d2"))

    def test_include_host_override(self):
        self._trigger_include_host_check(False)
        self._trigger_include_host_check(True)

    def _trigger_include_host_check(self, include_host):
        path = "/override_static_url/robots.txt?include_host=%s"
        response = self.fetch(path % int(include_host))
        self.assertEqual(response.body, utf8(str(True)))

    def test_static_304_if_modified_since(self):
        response1 = self.fetch("/static/robots.txt")
        response2 = self.fetch("/static/robots.txt", headers={
            'If-Modified-Since': response1.headers['Last-Modified']})
        self.assertEqual(response2.code, 304)
        self.assertTrue('Content-Length' not in response2.headers)
        self.assertTrue('Last-Modified' not in response2.headers)

    def test_static_304_if_none_match(self):
        response1 = self.fetch("/static/robots.txt")
        response2 = self.fetch("/static/robots.txt", headers={
            'If-None-Match': response1.headers['Etag']})
        self.assertEqual(response2.code, 304)


@wsgi_safe
class CustomStaticFileTest(WebTestCase):
    def get_handlers(self):
        class MyStaticFileHandler(StaticFileHandler):
            def get(self, path):
                path = self.parse_url_path(path)
                if path != "foo.txt":
                    raise Exception("unexpected path: %r" % path)
                self.write("bar")

            @classmethod
            def make_static_url(cls, settings, path):
                cls.get_version(settings, path)
                extension_index = path.rindex('.')
                before_version = path[:extension_index]
                after_version = path[(extension_index + 1):]
                return '/static/%s.%s.%s' % (before_version, 42, after_version)

            @classmethod
            def parse_url_path(cls, url_path):
                extension_index = url_path.rindex('.')
                version_index = url_path.rindex('.', 0, extension_index)
                return '%s%s' % (url_path[:version_index],
                                 url_path[extension_index:])

        class StaticUrlHandler(RequestHandler):
            def get(self, path):
                self.write(self.static_url(path))

        self.static_handler_class = MyStaticFileHandler

        return [("/static_url/(.*)", StaticUrlHandler)]

    def get_app_kwargs(self):
        return dict(static_path="dummy",
                    static_handler_class=self.static_handler_class)

    def test_serve(self):
        response = self.fetch("/static/foo.42.txt")
        self.assertEqual(response.body, b"bar")

    def test_static_url(self):
        with ExpectLog(gen_log, "Could not open static file", required=False):
            response = self.fetch("/static_url/foo.txt")
            self.assertEqual(response.body, b"/static/foo.42.txt")


@wsgi_safe
class HostMatchingTest(WebTestCase):
    class Handler(RequestHandler):
        def initialize(self, reply):
            self.reply = reply

        def get(self):
            self.write(self.reply)

    def get_handlers(self):
        return [("/foo", HostMatchingTest.Handler, {"reply": "wildcard"})]

    def test_host_matching(self):
        self.app.add_handlers("www.example.com",
                              [("/foo", HostMatchingTest.Handler, {"reply": "[0]"})])
        self.app.add_handlers(r"www\.example\.com",
                              [("/bar", HostMatchingTest.Handler, {"reply": "[1]"})])
        self.app.add_handlers("www.example.com",
                              [("/baz", HostMatchingTest.Handler, {"reply": "[2]"})])

        response = self.fetch("/foo")
        self.assertEqual(response.body, b"wildcard")
        response = self.fetch("/bar")
        self.assertEqual(response.code, 404)
        response = self.fetch("/baz")
        self.assertEqual(response.code, 404)

        response = self.fetch("/foo", headers={'Host': 'www.example.com'})
        self.assertEqual(response.body, b"[0]")
        response = self.fetch("/bar", headers={'Host': 'www.example.com'})
        self.assertEqual(response.body, b"[1]")
        response = self.fetch("/baz", headers={'Host': 'www.example.com'})
        self.assertEqual(response.body, b"[2]")


@wsgi_safe
class NamedURLSpecGroupsTest(WebTestCase):
    def get_handlers(self):
        class EchoHandler(RequestHandler):
            def get(self, path):
                self.write(path)

        return [("/str/(?P<path>.*)", EchoHandler),
                (u("/unicode/(?P<path>.*)"), EchoHandler)]

    def test_named_urlspec_groups(self):
        response = self.fetch("/str/foo")
        self.assertEqual(response.body, b"foo")

        response = self.fetch("/unicode/bar")
        self.assertEqual(response.body, b"bar")


@wsgi_safe
class ClearHeaderTest(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            self.set_header("h1", "foo")
            self.set_header("h2", "bar")
            self.clear_header("h1")
            self.clear_header("nonexistent")

    def test_clear_header(self):
        response = self.fetch("/")
        self.assertTrue("h1" not in response.headers)
        self.assertEqual(response.headers["h2"], "bar")


@wsgi_safe
class Header304Test(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            self.set_header("Content-Language", "en_US")
            self.write("hello")

    def test_304_headers(self):
        response1 = self.fetch('/')
        self.assertEqual(response1.headers["Content-Length"], "5")
        self.assertEqual(response1.headers["Content-Language"], "en_US")

        response2 = self.fetch('/', headers={
            'If-None-Match': response1.headers["Etag"]})
        self.assertEqual(response2.code, 304)
        self.assertTrue("Content-Length" not in response2.headers)
        self.assertTrue("Content-Language" not in response2.headers)
        # Not an entity header, but should not be added to 304s by chunking
        self.assertTrue("Transfer-Encoding" not in response2.headers)


@wsgi_safe
class StatusReasonTest(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            reason = self.request.arguments.get('reason', [])
            self.set_status(int(self.get_argument('code')),
                            reason=reason[0] if reason else None)

    def get_http_client(self):
        # simple_httpclient only: curl doesn't expose the reason string
        return SimpleAsyncHTTPClient(io_loop=self.io_loop)

    def test_status(self):
        response = self.fetch("/?code=304")
        self.assertEqual(response.code, 304)
        self.assertEqual(response.reason, "Not Modified")
        response = self.fetch("/?code=304&reason=Foo")
        self.assertEqual(response.code, 304)
        self.assertEqual(response.reason, "Foo")
        response = self.fetch("/?code=682&reason=Bar")
        self.assertEqual(response.code, 682)
        self.assertEqual(response.reason, "Bar")
        with ExpectLog(app_log, 'Uncaught exception'):
            response = self.fetch("/?code=682")
        self.assertEqual(response.code, 500)


@wsgi_safe
class DateHeaderTest(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            self.write("hello")

    def test_date_header(self):
        response = self.fetch('/')
        header_date = datetime.datetime.strptime(response.headers['Date'],
                                                 "%a, %d %b %Y %H:%M:%S GMT")
        self.assertTrue(header_date - datetime.datetime.utcnow() <
                        datetime.timedelta(seconds=2))


@wsgi_safe
class RaiseWithReasonTest(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            raise HTTPError(682, reason="Foo")

    def get_http_client(self):
        # simple_httpclient only: curl doesn't expose the reason string
        return SimpleAsyncHTTPClient(io_loop=self.io_loop)

    def test_raise_with_reason(self):
        response = self.fetch("/")
        self.assertEqual(response.code, 682)
        self.assertEqual(response.reason, "Foo")
        self.assertIn(b'682: Foo', response.body)

    def test_httperror_str(self):
        self.assertEqual(str(HTTPError(682, reason="Foo")), "HTTP 682: Foo")


@wsgi_safe
class ErrorHandlerXSRFTest(WebTestCase):
    def get_handlers(self):
        # note that if the handlers list is empty we get the default_host
        # redirect fallback instead of a 404, so test with both an
        # explicitly defined error handler and an implicit 404.
        return [('/error', ErrorHandler, dict(status_code=417))]

    def get_app_kwargs(self):
        return dict(xsrf_cookies=True)

    def test_error_xsrf(self):
        response = self.fetch('/error', method='POST', body='')
        self.assertEqual(response.code, 417)

    def test_404_xsrf(self):
        response = self.fetch('/404', method='POST', body='')
        self.assertEqual(response.code, 404)


class GzipTestCase(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            if self.get_argument('vary', None):
                self.set_header('Vary', self.get_argument('vary'))
            self.write('hello world')

    def get_app_kwargs(self):
        return dict(gzip=True)

    def test_gzip(self):
        response = self.fetch('/')
        self.assertEqual(response.headers['Content-Encoding'], 'gzip')
        self.assertEqual(response.headers['Vary'], 'Accept-Encoding')

    def test_gzip_not_requested(self):
        response = self.fetch('/', use_gzip=False)
        self.assertNotIn('Content-Encoding', response.headers)
        self.assertEqual(response.headers['Vary'], 'Accept-Encoding')

    def test_vary_already_present(self):
        response = self.fetch('/?vary=Accept-Language')
        self.assertEqual(response.headers['Vary'],
                         'Accept-Language, Accept-Encoding')


@wsgi_safe
class PathArgsInPrepareTest(WebTestCase):
    class Handler(RequestHandler):
        def prepare(self):
            self.write(dict(args=self.path_args, kwargs=self.path_kwargs))

        def get(self, path):
            assert path == 'foo'
            self.finish()

    def get_handlers(self):
        return [('/pos/(.*)', self.Handler),
                ('/kw/(?P<path>.*)', self.Handler)]

    def test_pos(self):
        response = self.fetch('/pos/foo')
        response.rethrow()
        data = json_decode(response.body)
        self.assertEqual(data, {'args': ['foo'], 'kwargs': {}})

    def test_kw(self):
        response = self.fetch('/kw/foo')
        response.rethrow()
        data = json_decode(response.body)
        self.assertEqual(data, {'args': [], 'kwargs': {'path': 'foo'}})


@wsgi_safe
class ClearAllCookiesTest(SimpleHandlerTestCase):
    class Handler(RequestHandler):
        def get(self):
            self.clear_all_cookies()
            self.write('ok')

    def test_clear_all_cookies(self):
        response = self.fetch('/', headers={'Cookie': 'foo=bar; baz=xyzzy'})
        set_cookies = sorted(response.headers.get_list('Set-Cookie'))
        self.assertTrue(set_cookies[0].startswith('baz=;'))
        self.assertTrue(set_cookies[1].startswith('foo=;'))
