# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import dendrite

with open('README.rst') as f:
    readme = f.read()

with open('LICENCE') as f:
    licence = f.read()

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')


setup(
    name='dendrite',
    version=dendrite.__version__,
    description='Social connectivitiy as a library',
    long_description=readme,
    keywords='django social login registration oauth2',
    author='Alen Mujezinovic',
    author_email='alen@caffeinehit.com',
    url='https://github.com/caffeinehit/dendrite',
    license=licence,
    install_requires=install_requires,
    packages=find_packages(exclude=('tests', 'docs')),


)

