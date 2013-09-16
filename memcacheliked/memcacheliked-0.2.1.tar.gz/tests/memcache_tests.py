# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 by Vicious Red Beam
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import multiprocessing
import unittest
import memcache
import time
from memcacheliked.sample import SampleServer

class GetSetProtocol(unittest.TestCase):
    def setUp(self):
        self.server = SampleServer()
        self.server_process = multiprocessing.Process(target=self.server.start)
        self.server_process.start()
        time.sleep(0.1)
        self.c = memcache.Client(['127.0.0.1:11211'])

    def tearDown(self):
        self.server_process.terminate()

    def test_get_empty(self):
        self.assertTrue(self.c.get('wrong') is None)

    def test_set_get(self):
        self.c.set('right', 'blah')
        self.assertEquals('blah', self.c.get('right'))
    
    def test_multi_get(self):
        self.c.set('first', 'foo')
        self.c.set('second', 'bar')
        res = {'first': 'foo', 'second': 'bar'}
        self.assertEquals(res, self.c.get_multi(['first', 'second']))
    
    def test_multi_empty(self):
        self.assertEquals({}, self.c.get_multi(['wrong1', 'wrong2']))

    def test_delete(self):
        self.c.set('disappearing', 'aaa')
        self.c.delete('disappearing')
        self.assertEquals(None, self.c.get('disappearing'))
    
    def test_delete_multi(self):
        self.c.set('disappearing1', 'aaa')
        self.c.set('disappearing2', 'aaa')
        self.c.delete_multi(['disappearing1', 'disappearing2', 'wrong'])
        self.assertEquals({}, self.c.get_multi(['disappearing1', 'disappearing2', 'wrong']))

