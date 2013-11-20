# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages


setup(
    name='tango-capo',
    version='0.2',
    author=u'Tim Baxter',
    author_email='mail.baxter@gmail.com',
    packages=find_packages(),
    url='https://github.com/tBaxter/tango-capo',
    license='LICENCE.txt',
    description='Capo for Django.',
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False,
    #dependency_links = ['http://github.com/tBaxter/capo/tarball/master#egg=capo-0.3']
)
