import unittest
import byu_ws_sdk as oit
from byu_ws_sdk.core import _split_url, _sort_params


class TestOITWebServicesLibrary(unittest.TestCase):
    def test_url_encode_no_body(self):
        testSharedSecret = "kgBxqr5AmiPHQpN8J9VumHLJzTDHoeDbgzqawPTc"
        hmac = oit.url_encode(testSharedSecret, "http://www.byu.edu/", "")
        self.assert_(hmac and len(hmac) == 88)

    def test_url_encode_body_no_form(self):
        testSharedSecret = "kgBxqr5AmiPHQpN8J9VumHLJzTDHoeDbgzqawPTc"
        hmac = oit.url_encode(testSharedSecret, "http://www.byu.edu/", "test body content")
        self.assert_(hmac and len(hmac) == 88)

    def test_url_encode_body_form(self):
        testSharedSecret = "kgBxqr5AmiPHQpN8J9VumHLJzTDHoeDbgzqawPTc"
        hmac = oit.url_encode(testSharedSecret, "http://www.byu.edu/", "sar=2,pau=1,sar=6",
                              "application/x-www-form-urlencoded", "PUT")
        self.assert_(hmac and len(hmac) == 88)

    def test__split_url(self):
        host, rest = _split_url("http://www.byu.edu/testing/123?p=1&q=true")
        self.assert_(host == "www.byu.edu")
        self.assert_(rest == "/testing/123")
        host, rest = _split_url("https://www.byu.edu/testing/123?p=1&q=true")
        self.assert_(host == "www.byu.edu")
        self.assert_(rest == "/testing/123")
        host, rest = _split_url("https://peter.byu.edu")
        self.assert_(host == "peter.byu.edu")
        self.assert_(rest == "/")
        host, rest = _split_url("https://www.byu.edu:8443/testing/123?p=1&q=true")
        self.assert_(host == "www.byu.edu")
        self.assert_(rest == "/testing/123")

    def test__sort_params(self):
        rv = _sort_params("p=1&a=9&a=0")
        self.assert_(rv == "a=9,0&p=1")
        rv = _sort_params("")
        self.assert_(rv == "")
        rv = _sort_params("i=paul&done=true")
        self.assert_(rv == "done=true&i=paul")
        rv = _sort_params("done=true")
        self.assert_(rv == "done=true")

    def test_nonce_encode(self):
        nonceValue = u's9dg3yRQx1rAeH7Tkvd8bn8yi6ZN8G0mKYq5LzhQE5acr4g2Z4x6qpDmcA3owf3DmsozwUtqch/F2bBG6uJNjA=='
        sharedSecret = '98F8wh62cAt8OuufF2rY3B1MSelA8MArV_Zg4CJ9'
        hmac = oit.nonce_encode(sharedSecret, nonceValue)
        self.assert_(len(hmac) == 88)

    def test_get_http_authorization_header(self):
        apiKey = 'YF4i2Qdx2WuSj-G8583M'
        sharedSecret = '98F8wh62cAt8OuufF2rY3B1MSelA8MArV_Zg4CJ9'
        headerValue1 = oit.get_http_authorization_header(apiKey, sharedSecret, "WsSession", "URL",
                                                         "http://www.byu.edu/", "")
        headerValue2 = oit.get_http_authorization_header(apiKey, sharedSecret, "WsSession", "URL",
                                                         "http://www.byu.edu/", "test body data")
        self.assert_(headerValue1)
        self.assert_(headerValue2)
        self.assert_(headerValue1 != headerValue2)


if __name__ == "__main__":
    unittest.main()
