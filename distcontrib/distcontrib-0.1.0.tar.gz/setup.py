#!/usr/bin/env python

ESSENTIAL = [ 'distribute', 'version', 'Cython' ]
try:
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build
except:
    import distcontrib.bootstrap
    distcontrib.bootstrap.install_requirements( ESSENTIAL )

    # do it again
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build



 ##
# This block contains settings you will eventually need to change
###

import distcontrib as du

PACKAGE      = du.pkg_name
VERSION      = du.pkg_version
DESCRIPTION  = du.pkg_description
LICENSE      = du.pkg_license
URL          = du.pkg_url
AUTHOR       = du.pkg_author
AUTHOR_EMAIL = du.pkg_email
KEYWORDS     = du.pkg_keywords
REQUIREMENTS = du.pkg_requirements
LONG_DESCRIPTION = du.tools.read('README')
CLASSIFIERS      = [ 'License :: ' + LICENSE,
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Cython',
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Environment :: Console' ]


 ##
# From this point on, it's unlikely you will be changing anything.
###

PACKAGES      = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])
PACKAGES_DATA = du.tools.findall_package_data(PACKAGES)
EXT_MODULES   = du.tools.find_ext_modules(PACKAGES)

setup(
    name=PACKAGE,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    package_data=PACKAGES_DATA,
    zip_safe=False,
    cmdclass={ 'build_ext' : cython_build,
               'doctest'   : du.doctest,
               'zap'       : du.zap, },
    ext_modules=EXT_MODULES,
    install_requires= ESSENTIAL + REQUIREMENTS
)
