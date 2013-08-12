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
    url='http://pypi.wfp.org/pypi/%s/' % app.NAME,

    author='UN World Food Programme',
    author_email='pasport.competence.centre@wfp.org',
    license="WFP Property",
    description='mocca',

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
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers'
    ]
)
