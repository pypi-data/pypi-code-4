#!/usr/bin/env python
try:
    from setuptools import setup 
except ImportError, err:
    from distutils.core import setup

from dox import VERSION

setup(
    name='Axilent-Dox',
    version='.'.join(map(str,VERSION)),
    description='Markdown-oriented content authoring for Axilent.',
    packages=['dox'],
    include_package_data=True,
    license='BSD',
    author='Loren Davie',
    author_email='code@axilent.com',
    url='https://github.com/Axilent/Dox',
    install_requires=['sharrock-client','Markdown==2.0.1'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Text Processing',
    ],
    scripts=['scripts/dox'],
)