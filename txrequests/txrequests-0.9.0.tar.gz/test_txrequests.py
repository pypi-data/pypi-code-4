#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Requests."""

from requests import Response
from os import environ
from txrequests import Session
from twisted.trial.unittest import TestCase
from twisted.internet import defer

HTTPBIN = environ.get('HTTPBIN_URL', 'http://httpbin.org/')

def httpbin(*suffix):
    """Returns url for HTTPBIN resource."""
    return HTTPBIN + '/'.join(suffix)


class RequestsTestCase(TestCase):

    @defer.inlineCallbacks
    def test_session(self):
        # basic futures get
        with Session() as sess:
            d = sess.get(httpbin('get'))
            self.assertIsInstance(d, defer.Deferred)
            resp = yield d
            self.assertIsInstance(resp, Response)
            self.assertEqual(200, resp.status_code)

            # non-200, 404
            d = sess.get(httpbin('status/404'))
            resp = yield d
            self.assertEqual(404, resp.status_code)

            def cb(s, r):
                self.assertIsInstance(s, Session)
                self.assertIsInstance(r, Response)
                # add the parsed json data to the response
                r.data = r.json()
                return r

            d = sess.get(httpbin('get'), background_callback=cb)
            # this should block until complete
            resp = yield d
            self.assertEqual(200, resp.status_code)
            # make sure the callback was invoked
            self.assertTrue(hasattr(resp, 'data'))

            def rasing_cb(s, r):
                raise Exception('boom')

            d = sess.get(httpbin('get'), background_callback=rasing_cb)
            raised = False
            try:
                resp = yield d
            except Exception as e:
                self.assertEqual('boom', e.args[0])
                raised = True
            self.assertTrue(raised)

    def test_max_workers(self):
        """ Tests the `max_workers` shortcut. """
        from twisted.python.threadpool import ThreadPool

        with Session() as session:
            self.assertEqual(session.pool.max, 4)
        with Session(maxthreads=5) as session:
            self.assertEqual(session.pool.max, 5)
        with Session(pool=ThreadPool(maxthreads=10)) as session:
            self.assertEqual(session.pool.max, 10)
        with Session(pool=ThreadPool(maxthreads=10),
                                     maxthreads=5) as session:
            self.assertEqual(session.pool.max, 10)

    @defer.inlineCallbacks
    def test_redirect(self):
        """ Tests for the ability to cleanly handle redirects. """
        with Session() as sess:
            d = sess.get(httpbin('redirect-to?url=get'))
            resp = yield d
            self.assertIsInstance(resp, Response)
            self.assertEqual(200, resp.status_code)

            d = sess.get(httpbin('redirect-to?url=status/404'))
            resp = yield d
            self.assertEqual(404, resp.status_code)

