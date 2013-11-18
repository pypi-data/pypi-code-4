#! /usr/bin/env python

from setuptools import setup
import sys

# Choose version of guess-language library (two separate implementations)
_PYLE26 = sys.version_info[0:2] <= (2,6)
guess_language = 'guess-language>=0.2' if _PYLE26 else 'guess_language-spirit>=0.5a4'

setup(
    name='mdx_smartypants',
    version='1.5.1',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Python-Markdown extension using smartypants to emit typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.',
    long_description=open('README.rst').read(),
    url='http://bitbucket.org/jeunice/mdx_smartypants',
    packages=['mdx_smartypants'],

    install_requires=['Markdown>=2.0', 'namedentities==1.5.2', guess_language],
    tests_require = ['tox', 'pytest', 'six', 'textdata'],
    zip_safe = False,
    keywords='markdown smartypants extension curly quotes typographic',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
