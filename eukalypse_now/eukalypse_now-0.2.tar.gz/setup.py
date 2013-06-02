#!/usr/bin/env python
"""
eukalypse_now

web server for eukalypse. 

:copyright: (c) 2012 Dennis Schwertel, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

tests_require = [
    'tox'
]

dependency_links = [
#    'http://github.com/kinkerl/eukalypse/tarball/master#egg=eukalypse',
#    'https://github.com/dcramer/logan/tarball/master#egg=logan'
]


install_requires = [
    'South==0.8.1',
    'Sphinx==1.2b1',
    'Pillow==2.0.0',
    'raven==3.3.7',
    'logan==0.5.6',
    'gunicorn==0.17.4',
    'eukalypse',
    'easy-thumbnails==1.2',
    'Django==1.4',
    'django-celery==3.0.17',
    'celery==3.0.19',
]

setup(
    name='eukalypse_now',
    version='0.2',
    author='Dennis Schwertel',
    author_email='s@digitalkultur.net',
    description='eukalypse web server',
    long_description=__doc__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': Tox},
    dependency_links = dependency_links,
    license='BSD',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'eukalypse_now = eukalypse_now.utils.runner:main',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
