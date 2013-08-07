#!/usr/bin/env python

ESSENTIAL = [ 'distcontrib' ]

def install_requirements(requirements, verbose=True):
    import os, pip
    pip_args = list()
    if verbose:
        print('Installing requirements: ' + str(requirements))
        pip_args.append( '--verbose' )
    proxy = os.environ['http_proxy']
    if proxy:
        pip_args.append('--proxy')
        pip_args.append(proxy)
        if verbose:
            print('http_proxy=' + proxy)
    pip_args.append('install')
    for req in requirements:
        pip_args.append( req )
    pip.main(initial_args = pip_args)

try:
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build
    import distcontrib as du
except:
    install_requirements( ESSENTIAL )

    # do it again
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build
    import distcontrib as du


##
# This block contains settings you will eventually need to change
##

import mantis2xml as myapp

PACKAGE      = myapp.pkg_name
VERSION      = myapp.pkg_version
DESCRIPTION  = myapp.pkg_description
LICENSE      = myapp.pkg_license
URL          = myapp.pkg_url
AUTHOR       = myapp.pkg_author
AUTHOR_EMAIL = myapp.pkg_email
KEYWORDS     = myapp.pkg_keywords
REQUIREMENTS = myapp.pkg_requirements
LONG_DESCRIPTION = du.tools.read('README')
CLASSIFIERS      = [ 'License :: ' + LICENSE,
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Cython',
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Environment :: Console' ]

##
# From this point on, it's very unlikely you will be interested on changing
# anything. One possible exception is if you are interested on running
# configuration scripts.
##

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
    cmdclass={'build_ext': cython_build,
              'doctest':   du.doctest,
              'zap':       du.zap, },
    ext_modules=EXT_MODULES,
    test_suite='test',
    install_requires=ESSENTIAL + REQUIREMENTS
)
