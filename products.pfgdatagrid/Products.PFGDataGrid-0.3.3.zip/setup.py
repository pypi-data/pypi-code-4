# -*- coding: utf-8 -*-
"""
This module contains the tool of Products.PFGDataGrid
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3.3'

long_description = (
    read('README.txt')
    + '\n\n' +
    'Change history\n'
    '**************\n'
    + '\n\n' +
    read('CHANGES.txt')
)


setup(
    name='Products.PFGDataGrid',
    version=version,
    description="Data-grid Field for PloneFormGen",
    long_description=long_description,
    classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
    keywords='Plone PloneFormGen',
    author='Steve McMahon',
    author_email='steve@dcn.org',
    url='http://plone.org/products/ploneformgen',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', ]),
    namespace_packages=['Products', ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.PloneFormGen',
        'Products.DataGridField',
    ],
    entry_points="""
    # -*- entry_points -*-
    """,
)
