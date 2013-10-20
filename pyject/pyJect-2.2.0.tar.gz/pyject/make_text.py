'''
	pyject.make_text.py
'''
from data import USER, EMAIL

def make_main(fileName):
    txt = '''

def {0}():
    pass

def test():
    pass

def main():
    {0}()

if __name__ == "__main__":
    main()
    '''.format(fileName)
    return txt

def make_test(fileName):
    txt = '''

import unittest

class Test{0}(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_{}(self):
        assertTrue(True)
	
if __name__ == "__main__":
    unittest.main()

    '''.format(fileName)
    return txt

def make_setup(name):
    txt = '''
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': ,
    'version': '0.0.1',
    'author': 'Kyle Roux',
    'author_email': 'jstacoder@gmail.com',
    'description': '',
    'long_description': open('README','r').read(),
    'py_packages': 
    }
setup(**config)
    '''
    return txt
