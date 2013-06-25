""" The module tests the main package functionality """

import time
import unittest2 as unittest
from itertools import imap
from multiprocessing import Process
from multiprocessing.connection import Listener
from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from urllib2 import HTTPError

from plone.testing.z2 import Browser

from collective.error.detector import config
from collective.error.detector.memoize import Sender, setupClient
from collective.error.detector.testing import\
    COLLECTIVE_ERROR_DETECTOR_FUNCTIONAL

# It's used for creating request structure (see requestutils.py).
REQUEST_FIELDS = ['user', 'time', 'path_info', 'data', 'method', 'headers']
TIMEOUT = 1
LOGFILE = 'logfile'
# change the critical status code for testing
config.CRITICAL_RESPONSE_STATUS = '4'


def logger(logfile=LOGFILE):
    """ Create an appropriate listener which subtitutes
        collective.recipe.logger
    """
    server = Listener(('127.0.0.1', DEFAULT_TCP_LOGGING_PORT))
    lfile = open(logfile, 'w', 0)
    while True:
        conn = server.accept()
        while True:
            try:
                data = conn.recv()
            except EOFError:
                break
            else:
                print >>lfile, data
        conn.close()


def readline(logs=LOGFILE):
    return open(logs).readline().strip()


class TestDetector(unittest.TestCase):
    """ Class tests the subscribers. You can see them in *.zcml. """

    layer = COLLECTIVE_ERROR_DETECTOR_FUNCTIONAL

    def setUp(self):
        self.portal_url = self.layer['portal'].absolute_url()
        self.browser = Browser(self.layer['app'])
        self.logger = Process(target=logger)
        self.logger.start()
        Sender.conn = setupClient()

    def tearDown(self):
        self.logger.terminate()
        Sender.conn.close()

    def test_successfulRequests(self):
        """ Method sends successfull requests and checks logs """
        self.browser.open(self.portal_url)
        request = readline()
        self.assertTrue(all(imap(lambda x: x in request, REQUEST_FIELDS)))

    def test_failedRequests(self):
        """ Method sends the failed requests and checks logs """
        try:
            self.browser.open(self.portal_url + '/Hi')
        except HTTPError:
            #XXX: wait for logger
            time.sleep(TIMEOUT)
            request = readline()
            self.assertTrue(all(imap(lambda x: x in request, REQUEST_FIELDS)))
            self.assertTrue("'status': '404'" in request)

    def test_formFilter(self):
        """ Method sends the request (post) and checks logs """
        # try to post data
        self.browser.post(self.portal_url, 'x=1&y=2')
        # check storage
        request = readline()
        self.assertTrue(all(imap(lambda x: x in request, REQUEST_FIELDS)))
        self.assertTrue("{'y': '2', 'x': '1'}" in request)

    def test_isRequestSuitable(self):
        """ Method sends unsuitable requests """
        # don't log this request
        url = '/portal_css/Sunburst Theme/member.css'
        self.browser.open(self.portal_url + url)
        self.assertEqual(readline(), '')
        # don't log this one too
        url = '/portal_css/Sunburst Theme/plone.kss'
        self.browser.open(self.portal_url + url)
        self.assertEqual(readline(), '')


class TestMemoizetion(unittest.TestCase):
    """ Class tests the memoizetion (memoize.py) """

    def setUp(self):
        self.logger = Process(target=logger)
        self.logger.start()
        Sender.conn = setupClient()

    def test_performance(self):
        """ Simple speed test """
        conn = Sender.sendData()
        start = time.time()
        conn.send('Test')
        end = time.time()
        # This test shows about 0.00018.
        # Let's set 0.01 for safety.
        self.assertTrue(end - start < 0.01)
        #XXX: wait for logger
        time.sleep(TIMEOUT)
        self.assertEqual(readline(), 'Test')

    def tearDown(self):
        self.logger.terminate()
        Sender.conn.close()
