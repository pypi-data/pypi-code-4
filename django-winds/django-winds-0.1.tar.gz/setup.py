#!/usr/bin/env python
from setuptools import setup, find_packages
import os

# Utility function to read README file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='django-winds',
    version='0.1',
    description='A tool to collect and serve wind prediction data.',
    author='Benjamin Stookey',
    author_email='ben@bilgecode.org',
    url='https://bitbucket.org/bilgecode/django-winds',
    license='LICENSE',
    long_description=read("README.rst"),
    packages=[
        'django_winds',
        'django_winds.backends',
    ],
    install_requires=[
        "Django >= 1.3",
        "setuptools",
        "django-tastypie >= 0.9",
        "beautifulsoup4 >= 4.1",
        "requests >= 1.2",
        "lxml >= 3.2"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
