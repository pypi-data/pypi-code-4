#!python

import os
import io

import py.test

test_dir = os.path.dirname(__file__)

@py.test.skip("fails on Python 3")
def test_bolivia_handler():
	from jaraco.net.whois import BoliviaWhoisHandler
	handler = BoliviaWhoisHandler('microsoft.com.bo')
	handler.client_address = '127.0.0.1'
	test_result = os.path.join(test_dir, 'nic.bo.html')
	handler._response = open(test_result).read()
	result = io.StringIO()
	handler.ParseResponse(result)
	assert 'Microsoft Corporation' in result.getvalue()
