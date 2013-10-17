#!/usr/bin/env python3
from setuptools import setup, find_packages

# work around error in atexit when running ./setup.py test
# see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html
import multiprocessing


setup(
    name='git-orm',
    version=__import__('git_orm').__version__,
    author='Martin Natano',
    author_email='natano@natano.net',
    description='object-relational mapper for the git object store',
    url='http://github.com/natano/git-orm/',
    long_description='',
    license='ISC',
    keywords=['Git', 'Distributed', 'ORM', 'Relational'],
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Database',
        'Topic :: Software Development :: Version Control',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 3 - Alpha',
    ],
    install_requires=['pygit2==0.19.1', 'distribute'],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
)
