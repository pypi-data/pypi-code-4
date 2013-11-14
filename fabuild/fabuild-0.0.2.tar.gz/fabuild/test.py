"""
Unit tests for fabric build
"""
import logging
import os
import shutil
import unittest

from concat import concat
from watch import watch
from clean import clean
from coffee import coffee
from util import get_files

logger = logging.getLogger(__name__)


class TestBuild(unittest.TestCase):

    dirs = [
        '/tmp/test_fab_build/1/2/3/',
        '/tmp/test_fab_build/1/test/',
        '/tmp/test_fab_build/coffee/'
    ]

    files = [
        '/tmp/test_fab_build/test.txt',
        '/tmp/test_fab_build/test.py',
        '/tmp/test_fab_build/1/one.py',
        '/tmp/test_fab_build/1/2/two.py',
        '/tmp/test_fab_build/1/2/3/three.py',
        '/tmp/test_fab_build/1/2/3/three.py',
        '/tmp/test_fab_build/coffee/test1.coffee',
        '/tmp/test_fab_build/coffee/test2.coffee',
        '/tmp/test_fab_build/coffee/test3.coffee'
    ]

    def setUp(self):
        try:
            shutil.rmtree('/tmp/test_fab_build/')
        except:
            pass

        for d in self.dirs:
            os.makedirs(d)

        for f in self.files:
            with open(f, 'a') as x:
                if f.endswith('coffee'):
                    x.write('console.log "hello"')

    def tearDown(self):
        if 'KEEP' in os.environ:
            print "Keeping all test data"
            return

        for d in self.dirs:
            try:
                shutil.rmtree(d)
            except:
                pass

    def test_get_files(self):

        paths = get_files('/tmp/test_fab_build/test.txt')
        expected = ['/tmp/test_fab_build/test.txt']
        self.assertItemsEqual(paths, expected)

        paths = get_files(dict(path='/tmp/test_fab_build/', recursive=False))
        expected = ['/tmp/test_fab_build/test.txt',
                    '/tmp/test_fab_build/test.py',
                    '/tmp/test_fab_build/coffee',
                    '/tmp/test_fab_build/1']
        self.assertItemsEqual(paths, expected)

        paths = get_files(dict(path='/tmp/test_fab_build/', match=["*.py",], recursive=False))
        expected = ['/tmp/test_fab_build/test.py']
        self.assertItemsEqual(paths, expected)

        paths = get_files(dict(path='/tmp/test_fab_build/', ignore=["*.py",], recursive=False))
        expected = ['/tmp/test_fab_build/test.txt',
                    '/tmp/test_fab_build/coffee',
                    '/tmp/test_fab_build/1']
        self.assertItemsEqual(paths, expected)

        paths = get_files(dict(path='/tmp/test_fab_build/', only_files=True, recursive=False))
        expected = ['/tmp/test_fab_build/test.txt',
                    '/tmp/test_fab_build/test.py']
        self.assertItemsEqual(paths, expected)

        paths = get_files(dict(path='/tmp/test_fab_build/'))
        expected = [
            '/tmp/test_fab_build/1',
            '/tmp/test_fab_build/1/2',
            '/tmp/test_fab_build/1/2/3',
            '/tmp/test_fab_build/1/test',
            '/tmp/test_fab_build/test.txt',
            '/tmp/test_fab_build/test.py',
            '/tmp/test_fab_build/1/one.py',
            '/tmp/test_fab_build/1/2/two.py',
            '/tmp/test_fab_build/coffee',
            '/tmp/test_fab_build/coffee/test1.coffee',
            '/tmp/test_fab_build/coffee/test2.coffee',
            '/tmp/test_fab_build/coffee/test3.coffee',
            '/tmp/test_fab_build/1/2/3/three.py'
        ]
        self.assertItemsEqual(paths, expected)

        paths = get_files(dict(path='/tmp/test_fab_build/', recursive=True, only_files=True))
        expected = [
            '/tmp/test_fab_build/test.txt',
            '/tmp/test_fab_build/test.py',
            '/tmp/test_fab_build/1/one.py',
            '/tmp/test_fab_build/1/2/two.py',
            '/tmp/test_fab_build/1/2/3/three.py',
            '/tmp/test_fab_build/coffee/test1.coffee',
            '/tmp/test_fab_build/coffee/test2.coffee',
            '/tmp/test_fab_build/coffee/test3.coffee'
        ]
        self.assertItemsEqual(paths, expected)

    def test_clean(self):
        clean(files=dict(path='/tmp/test_fab_build/', match=['*test.*'], ignore=['*.txt']))
        self.assertFalse(os.path.exists('/tmp/test_fab_build/test.py'))

        clean(files=dict(path='/tmp/test_fab_build/', recursive=True, match=['*.py']))
        for f in [x for x in self.files if x.endswith(".py")]:
            self.assertFalse(os.path.exists(f))

        clean(files=dict(path='/tmp/test_fab_build/', recursive=True, match=['*3']))
        self.assertFalse(os.path.exists('/tmp/test_fab_build/1/2/3'))

        clean(files=dict(path='/tmp/test_fab_build/'))
        for d in self.dirs:
            self.assertFalse(os.path.exists(d))
        for f in self.files:
            self.assertFalse(os.path.exists(f))

    def test_coffee(self):
        coffee(files=dict(path='/tmp/test_fab_build/coffee'))
        expected = [
            '/tmp/test_fab_build/coffee/test1.js',
            '/tmp/test_fab_build/coffee/test2.js',
            '/tmp/test_fab_build/coffee/test3.js'
        ]
        for x in expected:
            self.assertTrue(os.path.exists(x))

        clean(files=dict(path='/tmp/test_fab_build/coffee', ignore=['*.coffee']))

        coffee(files=dict(path='/tmp/test_fab_build/coffee', match=['*/test1*']))
        self.assertTrue(os.path.exists('/tmp/test_fab_build/coffee/test1.js'))
        self.assertFalse(os.path.exists('/tmp/test_fab_build/coffee/test2.js'))
        self.assertFalse(os.path.exists('/tmp/test_fab_build/coffee/test3.js'))

        clean(dict(path='/tmp/test_fab_build/coffee', ignore=['*.coffee']))

        coffee(dict(path='/tmp/test_fab_build/coffee'), map=True)
        expected = [
            '/tmp/test_fab_build/coffee/test1.js',
            '/tmp/test_fab_build/coffee/test2.js',
            '/tmp/test_fab_build/coffee/test3.js',
            '/tmp/test_fab_build/coffee/test1.map',
            '/tmp/test_fab_build/coffee/test2.map',
            '/tmp/test_fab_build/coffee/test3.map'
        ]
        for x in expected:
            self.assertTrue(os.path.exists(x))

        clean(dict(path='/tmp/test_fab_build/coffee', ignore=['*.coffee']))

        coffee(dict(path='/tmp/test_fab_build/coffee'),
               join='joined.js', output="/tmp/test_fab_build/coffee", map=True)
        self.assertTrue(os.path.exists('/tmp/test_fab_build/coffee/joined.js'))
        self.assertTrue(os.path.exists('/tmp/test_fab_build/coffee/joined.map'))

        clean(dict(path='/tmp/test_fab_build/coffee', ignore=['*.coffee']))



if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger.addHandler(ch)

    unittest.main()
