# -*- coding: utf-8 -*-
""" db2rest setup.py script """

# db2rest
# from db2rest import __version__

# system
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from os.path import join, dirname

__version__ = "0.1.1"
setup(
    name="db2rest",
    version=__version__,
    description='A HTTP REST API for relational databases',
    author='Nicola Palumbo',
    author_email='nikpalumbo@gmail.com',
    packages=['db2rest','db2rest.test'],
    url='https://bitbucket.org/nikpalumbo/db2rest',
    long_description=open('README.md').read(),
    install_requires=['sqlalchemy','mysql-python','werkzeug',
                      'simplejson','jinja2','python-ldap','sphinx'],
    test_suite='db2rest.test',
    keywords=['database', 'HTTP rest'],
    scripts=['scripts/db2rest-tests.py', 'scripts/db2rest-doc.py'],
    entry_points={'console_scripts': [
            'db2rest-run = db2rest.app:start']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        ],
)
