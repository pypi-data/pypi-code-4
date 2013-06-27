import pkgutil
from setuptools import setup
import sys


def get_packages():
    return [name for _, name, is_package in pkgutil.walk_packages('.') if name.startswith('testsuite') and is_package]

dependencies = ['nose2>=0.4.6', 'colorama>=0.2.5']

setup(
    name='testsuite-prettyprint-outcomes',
    version='0.1.0-alpha.1',
    packages=get_packages(),
    url='',
    license='BSD3',
    author='Omer Katz',
    author_email='omer.drow@gmail.com',
    description='testsuite-prettyprint-outcomes is a nose2 plugin that prettyprints test outcomes.',
    namespace_packages=['testsuite', 'testsuite.prettyprint'],
    install_requires=dependencies
)
