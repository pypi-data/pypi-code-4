# -*- coding: utf-8 -*-
"""Setup for plone.mls.listing package."""

import os
from setuptools import setup, find_packages

__version__ = '0.9.4'


setup(
    name='plone.mls.listing',
    version=__version__,
    description="Plone support for MLS Listings.",
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
            'raptus.article.core',
        ],
    ),
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'Plone',
        'collective.autopermission',
        'collective.prettyphoto',
        'mls.apiclient',
        'plone.app.dexterity [grok]',
        'plone.app.referenceablebehavior',
        'plone.app.relationfield',
        'plone.app.versioningbehavior',
        'plone.formwidget.captcha',
        'plone.mls.core >= 0.2',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
