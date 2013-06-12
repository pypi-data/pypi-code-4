#!/usr/bin/python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README-pypi.rst', 'r') as inp:
  sdict = {
    'long_description' : inp.read()
  }

execfile('grokpy/version.py', {}, sdict)

sdict.update({
    'name' : 'grokpy',
    'description' : 'Python client for Grok Prediction Service',
    'url': 'http://github.com/numenta/grok-py',
    'download_url' : 'https://pypi.python.org/packages/source/g/grokpy/grokpy-%s.tar.gz' % sdict['version'],
    'author' : 'Ian Danforth',
    'author_email' : 'idanforth@numenta.com',
    'maintainer' : 'Austin Marshall',
    'maintainer_email' : 'amarshall@groksolutions.com',
    'keywords' : ['groksolutions', 'numenta', 'prediction'],
    'license' : 'MIT',
    'install_requires': [
        'requests',
        'certifi',
        'nose'],
    'test_suite': 'tests.unit',
    'packages' : ['grokpy'],
    'classifiers' : [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
})

setup(**sdict)
