# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------

import time
import unittest
import requests
import pyojo
from pyojo.server import HTTPD

SERVER = "http://127.0.0.1"

ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"


class Browse(object):

    def __init__(self, url, method="GET", accept="*/*"):

        self.url = url
        self.method = method
        self.accept = accept
        self.session = requests.Session()
        headers = {"Accept": ACCEPT}
        self.prepped = requests.Request(method,
                                        url,
                               #data=data
                                        headers=headers,
                                        ).prepare()
        # do something with prepped.body
        # do something with prepped.headers
        self.response = self.session.send(self.prepped,
              #stream=stream,
              #verify=verify,
              #proxies=proxies,
              #cert=cert,
              #timeout=timeout
                            )
        if self.response.status_code!=200:
            print "Status Code %s" % self.response.status_code
        if self.response.encoding!="utf-8":
            print "Encoding %s" % self.response.encoding
            
        self.request = self.response.request
        try:
            self.ctype = self.response.headers['content-type']
        except KeyError:
            self.ctype = None
        try:
            self.handled = self.response.headers['x-handler']
        except KeyError:
            self.handled = None
        try:
            self.returns = self.response.headers['x-type']
        except KeyError:
            self.returns = None
        print "Handler %s returns %s (%s)" % (self.handled,
                                              self.ctype,
                                              self.returns)
        self.content = self.response.text
        


class RequestTest(unittest.TestCase):
    def setUp(self):
        """ The Config is not the same, is other process!
        """
        self.httpd = HTTPD()
        self.httpd.start()
        time.sleep(0.5)
        
    def tearDown(self):
        self.httpd.stop()