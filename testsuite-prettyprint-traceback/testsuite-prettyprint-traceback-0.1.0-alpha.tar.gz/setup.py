import pkgutil
from setuptools import setup
import sys


def get_packages():
    return [name for _, name, is_package in pkgutil.walk_packages('.') if name.startswith('testsuite') and is_package]

dependencies = ['nose2>=0.4.6', 'pygments>=1.6']

if sys.platform == 'win32':
    dependencies.append('colorama>=0.2.5')

setup(
    name='testsuite-prettyprint-traceback',
    version='0.1.0-alpha',
    packages=get_packages(),
    url='',
    license='BSD3',
    author='Omer Katz',
    author_email='omer.drow@gmail.com',
    description='testsuite-prettyprint-traceback is a nose2 plugin that prettyprints traceback on failures and errors.',
    namespace_packages=['testsuite', 'testsuite.prettyprint'],
    install_requires=dependencies
)
