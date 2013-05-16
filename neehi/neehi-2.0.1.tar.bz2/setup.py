#!/usr/bin/python

from distutils.core import setup

from test.testcommand import test

_long_description = """
This module provides a standard socket-like interface for Python
developers to tunnel connections through SOCKS4, SOCKS5, and
HTTP CONNECT proxies.
"""

setup(
    name = "neehi",
    version = "2.0.1",
    description = "A Python SOCKS module.",
    long_description = _long_description,
    url = "http://pypi.python.org/pypi/neehi",
    license = "BSD",
    maintainer = "Sean Robinson",
    maintainer_email = "seankrobinson@gmail.com",
    keywords = "SOCKS SOCKS4 SOCKS5 HTTP proxy",
    packages = ["neehi"],
    data_files=[('docs', ['docs/CHANGELOG', 'docs/LICENSE', 'docs/README',]),
                ('test', ['test/__init__.py',
                          'test/mocks.py',
                          'test/testcommand.py']),
                ('test/unit', ['test/unit/__init__.py',
                               'test/unit/cm.py',
                               'test/unit/excepts.py',
                               'test/unit/functions.py',
                               'test/unit/socksocket.py', ]),
               ],
    platforms = ["Linux", "MacOS", "Windows"],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: Proxy Servers',
    ],
    cmdclass={'test': test},
)

