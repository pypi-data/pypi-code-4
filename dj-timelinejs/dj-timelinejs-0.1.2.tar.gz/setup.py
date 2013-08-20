# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='dj-timelinejs',
    version='0.1.2',
    author='Ben Best',
    author_email='ben.best@gmail.com,',
    packages=['timelinejs'],
    include_package_data=True,
    url='https://github.com/azundo/dj-timelinejs/',
    license='BSD license and MPL 2.0, see LICENSE',
    description='Support for serving TimelineJS from Django sites.',
    long_description=open('README.md').read(),
)

