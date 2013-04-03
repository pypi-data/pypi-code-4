from setuptools import setup
import sys, os

from forgehg.version import __version__

TOOL_DESCRIPTION = """ForgeHg enables Allura installation to use Mercurial
source code management system. Mercurial (Hg) is an open source distributed
version control system (DVCS) similar to git and written in Python.
"""

setup(name='ForgeHg',
      version=__version__,
      description="Mercurial (Hg) SCM support for Allura open forge",
      long_description=TOOL_DESCRIPTION,
      classifiers=[
        ## From http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: TurboGears',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Bug Tracking'
      ],
      keywords='Allura forge Mercurial Hg scm',
      author_email='allura-dev@incubator.apache.org',
      url='http://sourceforge.net/p/forgehg',
      license='GPLv2',
      packages=[
        'forgehg',
        'forgehg.model',
        'forgehg.templates'
      ],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'Allura',
          'mercurial >= 1.4.1, <= 1.4.3',
      ],
      entry_points="""
      [allura]
      Hg=forgehg.hg_main:ForgeHgApp
      """,
      )
