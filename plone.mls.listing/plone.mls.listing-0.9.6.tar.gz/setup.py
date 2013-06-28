# -*- coding: utf-8 -*-
"""Setup for plone.mls.listing package."""

from setuptools import setup, find_packages

version = '0.9.6'
description = "Plone support for MLS Listings."
long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read()

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'Pillow',
    'collective.autopermission',
    'collective.prettyphoto',
    'mls.apiclient',
    'plone.app.dexterity [grok]',
    'plone.app.referenceablebehavior',
    'plone.app.relationfield',
    'plone.app.versioningbehavior',
    'plone.formwidget.captcha',
    'plone.mls.core >= 0.2',
]

setup(
    name='plone.mls.listing',
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
    url='https://github.com/propertyshelf/plone.mls.listing',
    download_url='http://pypi.python.org/pypi/plone.mls.listing',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.mls'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
            # 'raptus.article.core',
        ],
    ),
    install_requires=install_requires,
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
