# -*- coding: utf-8 -*-
"""Setup for plone.mls.core package."""

import os
from setuptools import setup, find_packages

__version__ = '0.4.1'


setup(
    name='plone.mls.core',
    version=__version__,
    description="Plone support for the Propertyshelf MLS.",
    long_description='\n\n'.join([
        open("README.txt").read() + "\n" +
        open(os.path.join("docs", "HISTORY.txt")).read(),
    ]),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Zope",
    ],
    keywords='plone zope mls listing',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://bitbucket.org/propertyshelf/plone.mls.core',
    download_url='http://pypi.python.org/pypi/plone.mls.core',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.mls'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    install_requires=[
        'setuptools',
        'Plone',
        'plone.app.registry',
        'httplib2',
        'simplejson',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
