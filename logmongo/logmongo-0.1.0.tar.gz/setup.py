# installation: easy_install logmongo
from setuptools import setup

requires = [
    'pymongo',
    'prettyprint',
]

setup( 
    name = 'logmongo',
    version = '0.1.0',
    description = 'Logmongo: Log messages to a capped MongoDB collections',
    keywords = 'Logmongo log dict messages mongo MongoDB',
    long_description = open('README').read(),

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/logmongo',

    platforms = ['All'],
    license = 'Public Domain',

    py_modules = ['logmongo'],
    include_package_data = True,

    install_requires = requires,
    scripts=['logmongo'],
)

"""
setup()
  keyword args: http://peak.telecommunity.com/DevCenter/setuptools

configure pypi username and password in ~/.pypirc::

 [pypi]
 username:
 password:


build and upload to pypi with this::

 python setup.py sdist bdist_egg register upload
"""
