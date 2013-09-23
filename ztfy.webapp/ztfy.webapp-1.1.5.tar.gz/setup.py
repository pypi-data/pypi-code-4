##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="ztfy.webapp",
    version='1.1.5',
    author="Thierry Florac",
    author_email="tflorac@ulthar.net",
    url="http://www.ztfy.org",
    description="ZTFY web application template",
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        + '\n\n' +
        'Download\n'
        '********'),
    license="ZPL",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Framework :: Zope3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        ],
    packages=find_packages("src"),
    namespace_packages=['ztfy'],
    package_dir={"": "src"},
    package_data={"": [ '*.txt', '*.cfg', '*_tmpl', ]},
    zip_safe=False,
    include_package_data=True,
    install_requires=["setuptools", "PasteScript>=1.7.3"],
    extras_require={"test": ["zc.buildout", "zope.testing"]},
    entry_points={
        "paste.paster_create_template": [ "ztfy.webapp = ztfy.webapp.webapp_base.template:Webapp", ]
    })

