#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

f = open('README.md')
long_description = f.read().strip()
f.close()


requires = []

version = '0.1.5'

setup(
    name='fossrit_tahrir_theme',
    version=version,
    description="FOSSRIT theme for the Tahrir Open Badges webapp",
    long_description=long_description,
    author='David Gay',
    author_email='oddshocks@riseup.net',
    url='https://github.com/FOSSRIT/fossrit-tahrir-theme',
    license='GPLv3+',
    classifiers=[],
    install_requires=requires,
    packages=['fossrit_tahrir_theme'],
    include_package_data=True,
    zip_safe=False,
)
