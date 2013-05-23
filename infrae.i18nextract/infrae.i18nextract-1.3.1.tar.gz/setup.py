# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 50858 2013-05-23 11:19:23Z sylvain $

from setuptools import setup, find_packages
import os

name = 'infrae.i18nextract'


setup(
    name = name,
    version='1.3.1',
    author='Sylvain Viollon',
    author_email='info@infrae.com',
    description='Buildout recipe to extract i18n files in Silva',
    long_description=open('README.txt').read() + \
        open(os.path.join('docs', 'HISTORY.txt')).read(),
    url='https://svn.infrae.com/buildout/infrae.i18nextract/trunk/',
    license='ZPL 2.1',
    keywords='i18n extract formulator buildout',
    classifiers=[
        'Framework :: Buildout',
        'License :: OSI Approved :: Zope Public License',
        'Topic :: Software Development :: Version Control',
        ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages = ['infrae'],
    install_requires = [
        'zc.buildout',
        'zc.recipe.egg',
        'setuptools'],
    entry_points = {
        'zc.buildout': ['default = %s:Recipe' % name],
        }
    )
