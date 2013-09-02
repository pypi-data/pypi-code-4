#! /usr/bin/env python

from setuptools import setup
import sys

_PY3 = sys.version_info[0] >= 3


# A little black magic to install a different version of guess_language for py3.
# The updated version is not available on PyPI (yet), so must install directly
# from its code repository.
reqs = ['Markdown>=2.0', 'namedentities==1.5.2']
if _PY3:
    reqs.append('guess_language-spirit')
    dlinks = ['https://bitbucket.org/spirit/guess_language/downloads/guess_language-spirit-0.5a4.tar.bz2#egg=guess_language-spirit']
else:
    # But if py2, just get everything from PyPI, as usual.
    reqs.append('guess_language>=0.2')
    dlinks = []

setup(
    name='mdx_smartypants',
    version='1.5.0',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Python-Markdown extension using smartypants to emit typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.',
    long_description=open('README.rst').read(),
    url='http://bitbucket.org/jeunice/mdx_smartypants',
    packages=['mdx_smartypants'],
    install_requires=reqs,
    dependency_links=dlinks,
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
