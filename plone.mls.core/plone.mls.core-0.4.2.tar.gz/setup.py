# -*- coding: utf-8 -*-
"""Setup for plone.mls.core package."""

from setuptools import setup, find_packages

version = '0.4.2'
description = "Plone support for the Propertyshelf MLS."
long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

install_requires = [
    'setuptools',
    'plone.app.registry',
    'httplib2',
    'simplejson',
]

setup(
    name='plone.mls.core',
    version=version,
    description=description,
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='plone zope mls listing real estate',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/plone.mls.core',
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
    install_requires=install_requires,
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
