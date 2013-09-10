from distutils.core import setup
from setuptools import find_packages

setup(
    name='cmsplugin-section',
    version='0.1.0',
    author='Sasha Matijasic',
    author_email='sasha@selectnull.com',
    packages=find_packages(),
    # url='http://pypi.python.org/pypi/cmsplugin-section/',
    license='LICENSE',
    description='django-cms plugin for creating page sections with templates',
    long_description=open('README').read(),
    install_requires=['django-cms'],
)
