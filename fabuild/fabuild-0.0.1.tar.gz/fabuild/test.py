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
from util import _get_files

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

        paths = _get_files(path='/tmp/test_fab_build/test.txt')
        expected = {'/tmp/test_fab_build/test.txt'}
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/')
        expected = {'/tmp/test_fab_build/test.txt',
                    '/tmp/test_fab_build/test.py',
                    '/tmp/test_fab_build/coffee',
                    '/tmp/test_fab_build/1'}
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/', match=["*.py",])
        expected = {'/tmp/test_fab_build/test.py'}
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/', ignore=["*.py",])
        expected = {'/tmp/test_fab_build/test.txt',
                    '/tmp/test_fab_build/coffee',
                    '/tmp/test_fab_build/1'}
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/', only_files=True)
        expected = {'/tmp/test_fab_build/test.txt',
                    '/tmp/test_fab_build/test.py'}
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/', recursive=True)
        expected = {
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
        }
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/', recursive=True, ignore=["test*",])
        expected = {
            '/tmp/test_fab_build/1',
            '/tmp/test_fab_build/1/2',
            '/tmp/test_fab_build/1/2/3',
            '/tmp/test_fab_build/1/one.py',
            '/tmp/test_fab_build/1/2/two.py',
            '/tmp/test_fab_build/coffee',
            '/tmp/test_fab_build/1/2/3/three.py'
        }
        self.assertSetEqual(paths, expected)

        paths = _get_files(path='/tmp/test_fab_build/', recursive=True, only_files=True)
        expected = {
            '/tmp/test_fab_build/test.txt',
            '/tmp/test_fab_build/test.py',
            '/tmp/test_fab_build/1/one.py',
            '/tmp/test_fab_build/1/2/two.py',
            '/tmp/test_fab_build/1/2/3/three.py',
            '/tmp/test_fab_build/coffee/test1.coffee',
            '/tmp/test_fab_build/coffee/test2.coffee',
            '/tmp/test_fab_build/coffee/test3.coffee'
        }
        self.assertSetEqual(paths, expected)

    def test_clean(self):
        clean(dict(path='/tmp/test_fab_build/', match=['test.*'], ignore=['*.txt']))
        self.assertFalse(os.path.exists('/tmp/test_fab_build/test.py'))

        clean(dict(path='/tmp/test_fab_build/', recursive=True, match=['*.py']))
        for f in [x for x in self.files if x.endswith(".py")]:
            self.assertFalse(os.path.exists(f))

        clean(dict(path='/tmp/test_fab_build/', recursive=True, match=['3']))
        self.assertFalse(os.path.exists('/tmp/test_fab_build/1/2/3'))

        clean(dict(path='/tmp/test_fab_build/'))
        for d in self.dirs:
            self.assertFalse(os.path.exists(d))
        for f in self.files:
            self.assertFalse(os.path.exists(f))

    def test_coffee(self):
        coffee(dict(path='/tmp/test_fab_build/coffee'))
        expected = [
            '/tmp/test_fab_build/coffee/test1.js',
            '/tmp/test_fab_build/coffee/test2.js',
            '/tmp/test_fab_build/coffee/test3.js'
        ]
        for x in expected:
            self.assertTrue(os.path.exists(x))

        clean(dict(path='/tmp/test_fab_build/coffee', ignore=['*.coffee']))

        coffee(dict(path='/tmp/test_fab_build/coffee', match=['test1*']))
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

    def test_watch(self):

        pass  # Need to figure out how to test this, because of async
        # watch(coffee, path='/tmp/test_fab_build/coffee')
        # os.remove('/tmp/test_fab_build/coffee/test1.js')
        #
        # with open('/tmp/test_fab_build/coffee/test1.coffee', 'a') as x:
        #     x.write('console.log "hello"')
        #
        # self.assertTrue(os.path.exists('/tmp/test_fab_build/coffee/test1.js'))


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger.addHandler(ch)

    unittest.main()
