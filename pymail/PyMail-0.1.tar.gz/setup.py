#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "PyMail",
    version = "0.1",
    packages = find_packages(),
    install_requires = [
        'distribute',
        'docutils',
        'eventlet',
        'dnspython',
        'PyYAML',
        'Sphinx'
    ],
    package_data = {
        '': ['*.txt', '*.rst']
    },
    entry_points = {
        'console_scripts': [
            'smtpd = smtpd.main:main'
        ]
    },
    test_suite = 'nose.collector',
    test_requires = ['Nose'],
    author = "Johnny Wezel",
    author_email = "dev-jay@wezel.name",
    description = "An SMTP daemon",
    long_description = file('README.rst').read(),
    license = "GPL",
    platforms = 'POSIX',
    keywords = "mail smtp",
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
    ]
    #url = "http://example.com/HelloWorld/"
)
