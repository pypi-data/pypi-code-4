#!/usr/bin/env python
import os
import codecs
from setuptools import setup, find_packages

dirname = 'sample_data_utils'

app = __import__(dirname)


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(here, *parts), 'r').read()

tests_require = ['pytest', 'coverage', 'mock']
setup(
    name=app.NAME,
    version=app.get_version(),
    url='https://github.com/saxix/sample-data-utils',
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    license="MIT",
    description='Collections of utilities to create random "human readeable" sample data.',
    packages=find_packages('.'),
    include_package_data=True,
    install_requires=read('requirements.pip'),
    tests_require=tests_require,
    test_suite='conftest.runtests',
    extras_require={
        'tests': tests_require,
    },
    platforms=['linux'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers'
    ]
)
