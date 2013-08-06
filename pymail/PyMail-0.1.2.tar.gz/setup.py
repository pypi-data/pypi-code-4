#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "PyMail",
    version = "0.1.2",
    packages = find_packages(),
    install_requires = [
        'setuptools>=0.9.8',
        'docutils',
        'eventlet',
        'dnspython',
        'python-daemon',
        'PyYAML',
        'Sphinx'
    ],
    package_data = {
        '': ['*.txt', '*.rst', 'etc/pymail/*']
    },
    entry_points = {
        'console_scripts': [
            'pymail = pymail.main:main'
        ]
    },
    test_suite = 'nose.collector',
    tests_require = ['Nose'],
    author = "Johnny Wezel",
    author_email = "dev-jay@wezel.name",
    description = "An SMTP daemon",
    long_description = file('README.rst').read(),
    license = "GPL",
    platforms = 'POSIX',
    keywords = "mail smtp esmtp",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Topic :: Communications :: Email :: Post-Office :: IMAP'
    ],
    url = "https://pypi.python.org/pypi/PyMail"
)
