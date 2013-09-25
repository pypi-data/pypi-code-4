# coding: utf-8

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-relinking',
    version='0.0.1',
    packages=['django_relinking', 'django_relinking.migrations', 'django_relinking.templatetags'],
    install_requires=[
        'django>=1.4.5',
        'south>=0.7.6'
    ],
    include_package_data=True,
    license='BSD License',
    description='Provide relinking features.',
    long_description=README,
    url='http://django-relinking.beslave.net/',
    author='Vladislav Lozhechnik',
    author_email='lozhechnik.vladislav@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
