#!/usr/bin/env python
import os
from setuptools import setup, find_packages

dirname = 'pyppi'

app = __import__(dirname)
app.get_version()

def fread(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = fread('pyppi/requirements/install.pip').split('\n')
dev_requires = fread('pyppi/requirements/dev.pip').split('\n')
test_requires = fread('pyppi/requirements/testing.pip').split('\n')

postgres_requires = ['psycopg2>=2.4.0,<2.5.0', ]
mysql_requires = ['MySQL-python>=1.2.0,<1.3.0', ]

setup(
    name=app.NAME,
    version=app.get_version(),
    url='http://github.com/saxix/pyppi',
    author='sax',
    author_email='s.apostolico@gmail.com',
    keywords='django pypi packaging index',
    license="BSD",
    description="A Django application that emulates the Python Package Index",
    long_description=fread("README.txt"),

    test_suite='runtests.runtests',
    # package_dir={'': ''},
    packages=find_packages('.'),
    install_requires=install_requires,
    extras_require={
        'tests': test_requires,
        'dev': dev_requires,
        'postgres': install_requires + postgres_requires,
        'mysql': install_requires + mysql_requires,
    },
    tests_require = install_requires + test_requires,
    include_package_data = True,

    platforms=['linux'],
    scripts=['pyppi/bin/pyppi', ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
