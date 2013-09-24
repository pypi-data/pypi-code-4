#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock
from ilogue.readable import assertionMethod

class AssertableRequestTestCase(unittest.TestCase):

    def test_returnsDocument_Fails_on_nonexisting_page(self):
        from ilogue.readable import assertRequest
        reqForNonExistPage = assertRequest('http://httpbin.org/status/404')
        (assertionMethod(reqForNonExistPage.returnsDocument)
            .fails())

    def test_returnsDocument_Succeeds_on_existing_page(self):
        from ilogue.readable import assertRequest
        reqForExistPage = assertRequest('http://httpbin.org/get')
        (assertionMethod(reqForExistPage.returnsDocument)
            .doesNotFail())

    def test_returnsDocument_performs_post_if_set_to(self):
        from ilogue.readable import assertRequest
        reqPost = assertRequest('http://httpbin.org/post',method='POST')
        (assertionMethod(reqPost.returnsDocument)
            .doesNotFail())

    def test_returnsFile_returns_assertableFile(self):
        from ilogue.readable import assertRequest
        from ilogue.readable.AssertableFileResponse import AssertableFileResponse
        hdr = 'response-headers?Content-Disposition=attachment'
        reqPost = assertRequest('http://httpbin.org/'+hdr,method='GET') 
        f = reqPost.returnsFile()
        assert isinstance(f,AssertableFileResponse)



if __name__ == '__main__':
    unittest.main()
