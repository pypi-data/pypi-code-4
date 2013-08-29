#!/usr/bin/env python
from setuptools import setup, find_packages
import os


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
version = '0.2'
install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
]


setup(name='dragon-sphinx',
    version=version,
    description="Sphinx extensions for the Stupeflix tasks system",
    long_description=README,
    classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    keywords='dragon tasks sphinx documentation',
    author='Luper Rouch',
    author_email='luper.rouch@gmail.com',
    url='https://github.com/Stupeflix/dragon-sphinx',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires
)
