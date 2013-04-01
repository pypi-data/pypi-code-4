# -*- coding: utf-8 -*-
#
# This file is part of RestAuthCommon.
#
#    RestAuthCommon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RestAuthCommon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RestAuthCommon.  If not, see <http://www.gnu.org/licenses/>.

name = 'RestAuthCommon'
url = 'https://common.restauth.net'

import os
import re
import shutil
import sys
import unittest

from distutils.command.clean import clean as _clean
from subprocess import PIPE
from subprocess import Popen

try:
    from setuptools import Command
    from setuptools import setup
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import Command
    from setuptools import setup

LATEST_RELEASE = '0.6.1'

requires = ['pyyaml>=3.10', ]

if sys.version_info < (2, 6):
    print('ERROR: Sphinx requires at least Python 2.6 to run.')
    sys.exit(1)

if 'python' not in sys.path:
    sys.path.insert(0, 'python')

class build_doc(Command):
    description = "Build API documentation."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        version = get_version()
        sphinxopts = '-D release=%s -D version=%s' % (version, version)
        os.environ['SPHINXOPTS'] = sphinxopts
        os.environ['LATEST_RELEASE'] = LATEST_RELEASE

        cmd = ['make', '-C', 'doc', 'html']
        p = Popen(cmd)
        p.communicate()


def get_version():
    version = LATEST_RELEASE
    if os.path.exists('.version'):
        version = open('.version').readlines()[0]
    elif os.path.exists('.git'):  # get from git
        cmd = ['git', 'describe', 'master']
        p = Popen(cmd, stdout=PIPE)
        version = p.communicate()[0].decode('utf-8')
    elif os.path.exists('debian/changelog'):  # building .deb
        f = open('debian/changelog')
        version = re.search('\((.*)\)', f.readline()).group(1)
        f.close()

        if ':' in version:  # strip epoch:
            version = version.split(':', 1)[1]
        version = version.rsplit('-', 1)[0]  # strip debian revision
    return version.strip()


class version(Command):
    description = "Print version and exit."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(get_version())


class prepare_debian_changelog(Command):
    description = "prepare debian/changelog file"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not os.path.exists('debian/changelog'):
            sys.exit(0)

        version = get_version()
        cmd = ['sed', '-i', '1s/(.*)/(%s-1)/' % version, 'debian/changelog', ]
        p = Popen(cmd)
        p.communicate()


class clean(_clean):
    def run(self):
        cmd = ['make', '-C', 'doc', 'clean', ]
        p = Popen(cmd, stdout=PIPE)
        p.communicate()

        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('MANIFEST'):
            os.remove('MANIFEST')

        coverage = os.path.join('doc', 'coverage')
        if os.path.exists(coverage):
            print('rm -r %s' % coverage)
            shutil.rmtree(coverage)

        _clean.run(self)


class test(Command):
    description = "Run test suite."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import RestAuthCommon
        from RestAuthCommon import test
        unittest.main(RestAuthCommon)


class coverage(Command):
    description = "Run test suite and generate code coverage analysis."
    user_options = []

    def initialize_options(self):
        self.dir = os.path.join('doc', 'coverage')

    def finalize_options(self):
        pass

    def run(self):
        try:
            import coverage
        except ImportError:
            print("You need coverage.py installed.")
            return

        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        omit = [
            'python/RestAuthCommon/test.py',
        ]

        cov = coverage.coverage(cover_pylib=False, source=['python/RestAuthCommon', ],
                                branch=True, omit=omit)
        cov.start()

        import RestAuthCommon
        from RestAuthCommon import test
        unittest.main(RestAuthCommon, argv=['setup.py', 'test'], exit=False)

        cov.stop()
        cov.save()
        cov.html_report(directory=self.dir)


setup(
    name=name,
    version=str(get_version()),
    description='RestAuth shared library',
    author='Mathias Ertl',
    author_email='mati@restauth.net',
    platforms='any',
    url=url,
    download_url='http://git.fsinf.at/restauth/restauth-common',
    package_dir={'': 'python'},
    packages=['RestAuthCommon'],
    keywords=[],
    install_requires=requires,
    license="GNU General Public License (GPL) v3",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    cmdclass={
        'build_doc': build_doc,
        'clean': clean,
        'coverage': coverage,
        'version': version,
        'test': test,
        'prepare_debian_changelog': prepare_debian_changelog,
    },
    long_description="""RestAuthCommon is a small set of classes used by both
    `RestAuth server <https://server.restauth.net>`_ and `RestAuthClient
    <https://python.restauth.net>`_ (`PyPI
    <http://pypi.python.org/pypi/RestAuthClient/>`_)."""
)
