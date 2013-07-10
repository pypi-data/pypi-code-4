# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django_pynuodb',
    version='0.1',
    author='NuoDB',
    author_email='info@nuodb.com',
    description="NuoDB Extension for Django",
    keywords='nuodb django orm scalable cloud database',
    packages=['django_pynuodb'],
    package_dir={'django_pynuodb': 'django_pynuodb'},
    url='https://github.com/nuodb/nuodb-django',
    license='BSD licence, see LICENCE.txt',
    long_description=open('README.md').read(),
)