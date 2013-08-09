#!/usr/bin/env python

ESSENTIAL = [ 'distcontrib', 'hg+http://code.google.com/p/sqlalchemy-migrate' ]

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
    import migrate.versioning.api as dbmigrate
except:
    install_requirements( ESSENTIAL )

    # do it again
    from setuptools import find_packages
    from distutils.core import setup
    from Cython.Distutils import build_ext as cython_build
    import distcontrib as du
    import migrate.versioning.api as dbmigrate

##
# This block contains settings you will eventually need to change
##

import distcontrib_migrate as dm

PACKAGE      = dm.pkg_name
VERSION      = dm.pkg_version
DESCRIPTION  = dm.pkg_description
LICENSE      = dm.pkg_license
URL          = dm.pkg_url
AUTHOR       = dm.pkg_author
AUTHOR_EMAIL = dm.pkg_email
KEYWORDS     = dm.pkg_keywords
REQUIREMENTS = dm.pkg_requirements
LONG_DESCRIPTION = du.tools.read('README')
CLASSIFIERS      = [ 'License :: ' + LICENSE,
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Cython',
                     'Development Status :: 3 - Alpha',
                     'Intended Audience :: Developers',
                     'Environment :: Console' ]



##
# From this point on, it's very unlikedly you will be interested on changing
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
              'zap':       du.zap,
              'migrate':   dm.migrate,
              'psql':      dm.psql, },
    ext_modules=EXT_MODULES,
    install_requires=REQUIREMENTS,
)
