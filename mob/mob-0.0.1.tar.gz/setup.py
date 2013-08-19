# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import mob

with open('README.rst') as f:
    readme = f.read()

with open('LICENCE') as f:
    license = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='mob',
    version=mob.__version__,
    description='',
    long_description=readme,
    author='Alen Mujezinovic',
    author_email='alen@caffeinehit.com',
    url='https://github.com/caffeinehit/django-mob',
    license=license,
    install_requires=install_requires,
    packages=find_packages(exclude=('tests', 'docs'))
)

