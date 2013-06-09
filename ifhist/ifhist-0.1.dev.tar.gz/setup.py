import sys
from setuptools import setup

if sys.version_info < (2, 6):
    raise Exception('ifhist requires Python 2.6 or higher.')

# Todo: How does this play with pip freeze requirement files?
requires = []

# Python 2.6 does not include the argparse module.
try:
    import argparse
except ImportError:
    requires.append('argparse')

import ifhist as distmeta

setup(
    name='ifhist',
    version=distmeta.__version__,
    description='Gather usage statistics for network interfaces.',
    long_description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    license='MIT License',
    platforms=['any'],
    packages=['ifhist'],
    install_requires=requires,
    entry_points = {
        'console_scripts': [
            'ifstat = ifhist.ifstat:main'
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Networking :: Monitoring'
    ],
    keywords='network interface stats'
)
