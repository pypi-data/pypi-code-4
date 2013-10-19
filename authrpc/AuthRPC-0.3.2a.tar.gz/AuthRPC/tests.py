#!/usr/bin/env python

# Copyright (c) 2011-2012 Ben Croston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import unittest
import hashlib
from threading import Thread
import time
from wsgiref import simple_server
import platform
import urllib

IS_PY3 = platform.python_version().startswith('3')

try:
    urllib.urlopen('http://www.wyre-it.co.uk/')
    NO_INTERNET = False
except IOError:
    NO_INTERNET = True

##### server vvv #####
class api(object):
    def mymethod(self):
        return 'wibbler woz ere'

    def echo(self, mystring):
        return 'ECHO: ' + mystring

    def raiseexception(self):
        dividebyzeroerror = 1/0

    def returnnothing(self):
        pass

    def add(self, a, b):
        return a+b

def myauth(username, password, useragent=None):
    return username == 'testuser' and \
           password == hashlib.md5('s3cr3t'.encode()).hexdigest() and \
           useragent == 'AuthRPC_unittest'

def mybadauth(username, password, useragent=None):
    return 1 / 0  # generate exception

def make_server(api, auth, port):
    from server import AuthRPCApp
    class myhandler(simple_server.WSGIRequestHandler):
        def log_request(self, *a, **b):
            pass # do not output log messages
    application = AuthRPCApp(api, auth, filepath='')
    return simple_server.make_server('localhost', port, application, handler_class=myhandler)
##### server ^^^ #####

##### client vvv #####
class AuthTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, UnauthorisedError
        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='s3cr3t',
                                  user_agent='InternetExploiter')
        with self.assertRaises(UnauthorisedError):
            self.client.api.mymethod()

        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='wrongpassword',
                                  user_agent='AuthRPC_unittest')
        with self.assertRaises(UnauthorisedError):
            self.client.api.mymethod()

        self.client = ServerProxy('http://localhost:1337/',
                                  username='wronguser',
                                  password='s3cr3t',
                                  user_agent='AuthRPC_unittest')
        with self.assertRaises(UnauthorisedError):
            self.client.api.mymethod()

class BadAuthTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, RemoteException
        self.client = ServerProxy('http://localhost:1338/')
        with self.assertRaises(RemoteException):
            self.client.mymethod()

class BadBatchAuthTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, RemoteException, BatchCall
        self.client = ServerProxy('http://localhost:1338/')
        batch = BatchCall(self.client)
        batch.api.echo('One')
        batch.api.echo(mystring='Two')
        with self.assertRaises(RemoteException):
            batch()

@unittest.skipIf(NO_INTERNET, 'http://www.wyre-it.co.uk/ not contactable')
class NotFoundTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, NotFoundError
        self.client = ServerProxy('http://www.wyre-it.co.uk/this_should_generate_404.txt')
        with self.assertRaises(NotFoundError):
            self.client.api.mymethod()

class NetworkSocketTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, NetworkSocketError
        self.client = ServerProxy('http://localhost:666/')
        with self.assertRaises(NetworkSocketError):
            self.client.api.mymethod()

class AuthRPCTests(unittest.TestCase):
    def setUp(self):
        from client import ServerProxy
        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='s3cr3t',
                                  user_agent='AuthRPC_unittest')

class IgnoreClassNameTest(AuthRPCTests):
    def runTest(self):
        self.assertEqual(self.client.api.mymethod(),self.client.mymethod())

class ExceptionTest(AuthRPCTests):
    def runTest(self):
        from client import RemoteException
        with self.assertRaises(RemoteException):
            self.client.api.raiseexception()

class BadRequestTest(AuthRPCTests):
    def runTest(self):
        from client import BadRequestError
        with self.assertRaises(BadRequestError):
            self.client.api.FunctionDoesNotExist()

class EchoTest(AuthRPCTests):
    def runTest(self):
        if IS_PY3:
            POUND = '\u00A3'
        else:
            POUND = unicode('\u00A3')
        self.assertEqual(self.client.api.echo(POUND), 'ECHO: ' + POUND)
        self.assertEqual(self.client.api.echo('hello mum!'), 'ECHO: hello mum!')
        self.assertEqual(self.client.api.echo(mystring='wibble'), 'ECHO: wibble')

class AddTest(AuthRPCTests):
    def runTest(self):
        self.assertEqual(self.client.api.add(12,34), 46)
        self.assertEqual(self.client.api.add(1.2, 34), 35.2)

class ReturnNothing(AuthRPCTests):
    def runTest(self):
        self.assertEqual(self.client.api.returnnothing(), None)

class ProtocolErrorTest(AuthRPCTests):
    def runTest(self):
        from client import JSONRPCProtocolError
        with self.assertRaises(JSONRPCProtocolError):
            self.client.api.test(1, '2', three=3)

class FileTest(AuthRPCTests):
    def setUp(self):
        AuthRPCTests.setUp(self)

        # create big (100Mb) file
        self.tempfile = 'bigfile.tmp'
        with open(self.tempfile,'w') as f:
            for x in range(1024*100):
                f.write('x'*1024) # 1k of data

    def runTest(self):
        with open(self.tempfile,'rb') as f:
            servercopy = self.client.__getfile__(self.tempfile)
            for data in servercopy:
                source = f.read(len(data))
                self.assertEqual(data, source)

    def tearDown(self):
        AuthRPCTests.tearDown(self)
        os.remove(self.tempfile)

class NonExistentFileTest(AuthRPCTests):
    def runTest(self):
        from client import NotFoundError
        with self.assertRaises(NotFoundError):
            self.client.__getfile__('nonexistant.file')

class BadAuthFileTest(unittest.TestCase):
    def runTest(self):
        from client import ServerProxy, UnauthorisedError
        self.client = ServerProxy('http://localhost:1337/',
                                  username='testuser',
                                  password='s3cr3t',
                                  user_agent='InternetExploiter')
        with self.assertRaises(UnauthorisedError):
            self.client.__getfile__('LICENCE.txt')

class BatchTest(AuthRPCTests):
    def runTest(self):
        from client import BatchCall
        batch = BatchCall(self.client)
        batch.api.echo('One')
        batch.api.echo(mystring='Two')
        batch.echo('Three')
        batch.api.returnnothing()
        batch.api.add(9,1)
        self.assertEqual(batch(), ['ECHO: One', 'ECHO: Two', 'ECHO: Three', None, 10])

class BadBatchTest(AuthRPCTests):
    def runTest(self):
        from client import BatchCall, BadRequestError
        batch = BatchCall(self.client)
        batch.api.FunctionDoesNotExist()
        with self.assertRaises(BadRequestError):
            batch()

class SetFinishedFlag(unittest.TestCase):
    def runTest(self):
        global finished 
        finished = True
##### client ^^^ #####

def suite():
    global finished
    finished = False

    # create server 1
    def test_wrapper():
        server = make_server(api(), myauth, 1337)
        while not finished:
            server.handle_request()
    thread = Thread(target=test_wrapper)
    thread.start()
    
    # create server 2
    def test_wrapper():
        server = make_server(api(), mybadauth, 1338)
        while not finished:
            server.handle_request()
    thread = Thread(target=test_wrapper)
    thread.start()

    time.sleep(0.1) # wait for server threads to start

    # tests are as client
    suite = unittest.TestSuite()
    suite.addTest(AuthTest())
    suite.addTest(NotFoundTest())
    suite.addTest(NetworkSocketTest())
    suite.addTest(IgnoreClassNameTest())
    suite.addTest(ExceptionTest())
    suite.addTest(BadRequestTest())
    suite.addTest(EchoTest())
    suite.addTest(AddTest())
    suite.addTest(ReturnNothing())
    suite.addTest(ProtocolErrorTest())
    suite.addTest(FileTest())
    suite.addTest(NonExistentFileTest())
    suite.addTest(BadAuthFileTest())
    suite.addTest(BadAuthTest())
    suite.addTest(BatchTest())
    suite.addTest(SetFinishedFlag())
    suite.addTest(BadBatchTest())
    suite.addTest(BadBatchAuthTest())
    # btc fixme - test a list/tuple of api classes in another server
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

