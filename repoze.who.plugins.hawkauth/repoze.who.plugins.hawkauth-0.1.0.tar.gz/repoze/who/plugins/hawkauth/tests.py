# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
import time

from webob import Request
from webtest import TestApp

from zope.interface.verify import verifyClass

from repoze.who.interfaces import IIdentifier, IAuthenticator, IChallenger
from repoze.who.middleware import PluggableAuthenticationMiddleware

import hawkauthlib
import tokenlib

from repoze.who.plugins.hawkauth import HawkAuthPlugin, make_plugin


def make_environ(**kwds):
    environ = {}
    environ["wsgi.version"] = (1, 0)
    environ["wsgi.url_scheme"] = "http"
    environ["SERVER_NAME"] = "localhost"
    environ["SERVER_PORT"] = "80"
    environ["REQUEST_METHOD"] = "GET"
    environ["SCRIPT_NAME"] = ""
    environ["PATH_INFO"] = "/"
    environ.update(kwds)
    return environ


def dotted_name(name):
    """Return full dotted name of something in this module."""
    return "repoze.who.plugins.hawkauth.tests:" + name


def stub_application(environ, start_response):
    """Simple WSGI app that requires authentication.

    This is a simple testing app that returns the userid if the environment
    contains a repoze.who identity, and denies access if it does not. URLs
    containing the string "forbidden" will get a 403 response, while other
    URLs will get a 401 response.

    The special path "/public" can be viewed without authentication.
    """
    headers = [("Content-Type", "text/plain")]
    if environ["PATH_INFO"] == "/public":
        body = "public"
    else:
        if "repoze.who.identity" not in environ:
            if "forbidden" in environ["PATH_INFO"]:
                start_response("403 Forbidden", headers)
            else:
                start_response("401 Unauthorized", headers)
            return ["Unauthorized"]
        body = environ["repoze.who.identity"]["repoze.who.userid"]
        body = body.encode("utf8")
    start_response("200 OK", headers)
    return [body]


def stub_request_classifier(environ):
    """Testing request classifier; all requests are are just 'web' requests."""
    return "web"


def stub_challenge_decider(environ, status, headers):
    """Testing challenge decider; 401 and 403 responses get a challenge."""
    return status.split(None, 1)[0] in ("401", "403")


def stub_decode_hawk_id(request, id, **extra):
    """Stub hawk-id-decoding function that just returns the id itself."""
    data = {"userid": id}
    data.update(extra)
    return id, data


class TestHawkAuthPlugin(unittest.TestCase):
    """Testcases for the main HawkAuthPlugin class."""

    def setUp(self):
        self.plugin = HawkAuthPlugin()
        application = PluggableAuthenticationMiddleware(stub_application,
                                    [["hawk", self.plugin]],
                                    [["hawk", self.plugin]],
                                    [["hawk", self.plugin]],
                                    [],
                                    stub_request_classifier,
                                    stub_challenge_decider)
        self.app = TestApp(application)

    def _get_credentials(self, **data):
        id = tokenlib.make_token(data)
        key = tokenlib.get_token_secret(id)
        return {"id": id, "key": key}

    def test_implements(self):
        verifyClass(IIdentifier, HawkAuthPlugin)
        verifyClass(IAuthenticator, HawkAuthPlugin)
        verifyClass(IChallenger, HawkAuthPlugin)

    def test_make_plugin_can_explicitly_set_all_properties(self):
        plugin = make_plugin(
            decode_hawk_id=dotted_name("stub_decode_hawk_id"),
            nonce_cache="hawkauthlib:NonceCache")
        self.assertEquals(plugin.decode_hawk_id, stub_decode_hawk_id)
        self.assertTrue(isinstance(plugin.nonce_cache, hawkauthlib.NonceCache))

    def test_make_plugin_passes_on_args_to_nonce_cache(self):
        plugin = make_plugin(
            nonce_cache="hawkauthlib:NonceCache",
            nonce_cache_window=42)
        self.assertTrue(isinstance(plugin.nonce_cache, hawkauthlib.NonceCache))
        self.assertEquals(plugin.nonce_cache.window, 42)
        self.assertRaises(TypeError, make_plugin,
            nonce_cache="hawkauthlib:NonceCache",
            nonce_cache_invalid_arg="WHAWHAWHAWHA")

    def test_make_plugin_errors_out_on_unexpected_keyword_args(self):
        self.assertRaises(TypeError, make_plugin,
                                     unexpected="spanish-inquisition")

    def test_make_plugin_errors_out_on_args_to_a_non_callable(self):
        self.assertRaises(ValueError, make_plugin,
                                      nonce_cache=dotted_name("unittest"),
                                      nonce_cache_arg="invalidarg")

    def test_make_plugin_errors_out_if_decode_hawk_id_is_not_callable(self):
        self.assertRaises(ValueError, make_plugin,
                                      decode_hawk_id=dotted_name("unittest"))

    def test_make_plugin_produces_sensible_defaults(self):
        plugin = make_plugin()
        self.assertEquals(plugin.decode_hawk_id.im_func,
                          HawkAuthPlugin.decode_hawk_id.im_func)
        self.assertTrue(isinstance(plugin.nonce_cache, hawkauthlib.NonceCache))

    def test_make_plugin_curries_args_to_decode_hawk_id(self):
        plugin = make_plugin(
            decode_hawk_id=dotted_name("stub_decode_hawk_id"),
            decode_hawk_id_hello="hi")
        self.assertEquals(plugin.decode_hawk_id(None, "id")[0], "id")
        self.assertEquals(plugin.decode_hawk_id(None, "id")[1]["hello"], "hi")

    def test_remember_does_nothing(self):
        self.assertEquals(self.plugin.remember(make_environ(), {}), [])

    def test_forget_gives_a_challenge_header(self):
        headers = self.plugin.forget(make_environ(), {})
        self.assertEquals(len(headers), 1)
        self.assertEquals(headers[0][0], "WWW-Authenticate")
        self.assertTrue(headers[0][1] == "Hawk")

    def test_unauthenticated_requests_get_a_challenge(self):
        # Requests to most URLs generate a 401, which is passed through
        # with the appropriate challenge.
        r = self.app.get("/", status=401)
        challenge = r.headers["WWW-Authenticate"]
        self.assertTrue(challenge.startswith("Hawk"))
        # Requests to URLs with "forbidden" generate a 403 in the downstream
        # app, which should be converted into a 401 by the plugin.
        r = self.app.get("/forbidden", status=401)
        challenge = r.headers["WWW-Authenticate"]
        self.assertTrue(challenge.startswith("Hawk"))

    def test_authenticated_request_works(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        r = self.app.request(req)
        self.assertEquals(r.body, "test@moz.com")

    def test_authentication_fails_when_hawkid_has_no_userid(self):
        creds = self._get_credentials(hello="world")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        self.app.request(req, status=401)

    def test_authentication_with_non_hawk_scheme_fails(self):
        req = Request.blank("/")
        req.authorization = "OpenID hello=world"
        self.app.request(req, status=401)

    def test_authentication_without_hawkid_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        authz = req.environ["HTTP_AUTHORIZATION"]
        authz = authz.replace("id", "idd")
        req.environ["HTTP_AUTHORIZATION"] = authz
        self.app.request(req, status=401)

    def test_authentication_without_timestamp_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        authz = req.environ["HTTP_AUTHORIZATION"]
        authz = authz.replace("ts", "typostamp")
        req.environ["HTTP_AUTHORIZATION"] = authz
        self.app.request(req, status=401)

    def test_authentication_without_nonce_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        authz = req.environ["HTTP_AUTHORIZATION"]
        authz = authz.replace("nonce", "typonce")
        req.environ["HTTP_AUTHORIZATION"] = authz
        self.app.request(req, status=401)

    def test_authentication_with_expired_timestamp_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        ts = str(int(time.time() - 1000))
        req.authorization = ("Hawk", {"ts": ts})
        hawkauthlib.sign_request(req, **creds)
        self.app.request(req, status=401)

    def test_authentication_with_far_future_timestamp_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        ts = str(int(time.time() + 1000))
        req.authorization = ("Hawk", {"ts": ts})
        hawkauthlib.sign_request(req, **creds)
        self.app.request(req, status=401)

    def test_authentication_with_reused_nonce_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        # First request with that nonce should succeed.
        req = Request.blank("/")
        req.authorization = ("Hawk", {"nonce": "PEPPER"})
        hawkauthlib.sign_request(req, **creds)
        r = self.app.request(req)
        self.assertEquals(r.body, "test@moz.com")
        # Second request with that nonce should fail.
        req = Request.blank("/")
        req.authorization = ("Hawk", {"nonce": "PEPPER"})
        hawkauthlib.sign_request(req, **creds)
        self.app.request(req, status=401)

    def test_authentication_with_busted_hawkid_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        id = hawkauthlib.utils.parse_authz_header(req)["id"]
        authz = req.environ["HTTP_AUTHORIZATION"]
        authz = authz.replace(id, "XXX" + id)
        req.environ["HTTP_AUTHORIZATION"] = authz
        self.app.request(req, status=401)

    def test_authentication_with_busted_signature_fails(self):
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/")
        hawkauthlib.sign_request(req, **creds)
        signature = hawkauthlib.utils.parse_authz_header(req)["mac"]
        authz = req.environ["HTTP_AUTHORIZATION"]
        authz = authz.replace(signature, "XXX" + signature)
        req.environ["HTTP_AUTHORIZATION"] = authz
        self.app.request(req, status=401)

    def test_access_to_public_urls(self):
        # Request with no credentials is allowed access.
        req = Request.blank("/public")
        resp = self.app.request(req)
        self.assertEquals(resp.body, "public")
        # Request with valid credentials is allowed access.
        creds = self._get_credentials(username="test@moz.com")
        req = Request.blank("/public")
        hawkauthlib.sign_request(req, **creds)
        resp = self.app.request(req)
        self.assertEquals(resp.body, "public")
        # Request with invalid credentials gets a 401.
        req = Request.blank("/public")
        hawkauthlib.sign_request(req, **creds)
        signature = hawkauthlib.utils.parse_authz_header(req)["mac"]
        authz = req.environ["HTTP_AUTHORIZATION"]
        authz = authz.replace(signature, "XXX" + signature)
        req.environ["HTTP_AUTHORIZATION"] = authz
        resp = self.app.request(req, status=401)

    def test_authenticate_only_accepts_hawk_credentials(self):
        # Yes, this is a rather pointless test that boosts line coverage...
        self.assertEquals(self.plugin.authenticate(make_environ(), {}), None)
