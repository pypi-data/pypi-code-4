"""
Kibrit
------

SCM watcher tool. Get current revision and send update notify.
"""

import sys
from os import path as op

from setuptools import setup, find_packages

py_version = sys.version_info[:2]

PY3 = py_version[0] == 3

if PY3:
    if py_version < (3, 2):
        # raise RuntimeError('On Python 3, Kibrit requires Python 3.2 or better')
        raise RuntimeError('Havent Tested Kibrit on Python 3, \n'
                           '"Tread softly because you tread on my dreams."~W.B.Yeats')
else:
    if py_version < (2, 6):
        raise RuntimeError('On Python 2, Kibrit requires Python 2.6 or better')

def read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


NAME = 'django_kibrit'

CURDIR = op.dirname(__file__)
MODULE = __import__(NAME)
README = op.join(CURDIR, 'README.rst')
# REQUIREMENTS = open(op.join(CURDIR, 'requirements.txt')).readlines()
# if sys.version_info < (2, 7):
#     REQUIREMENTS.append('importlib')

setup(
    name=NAME,
    version=MODULE.__version__,
    license=MODULE.__license__,
    author=MODULE.__author__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),
    keywords = "git static revision django".split(),

    maintainer='sinanm89',
    maintainer_email='sinanm89@gmail.com',
    author_email='sinanm89@gmail.com',
    url=' http://github.com/sinanm89/kibrit',
    download_url = 'https://github.com/sinanm89/kibrit/tarball/0.1',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Natural Language :: Turkish',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Framework :: Django",
        'Programming Language :: Python :: 2.6',
        'Environment :: Console',
    ],
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False
)

# list of all the classifiers https://pypi.python.org/pypi?%3Aaction=list_classifiers