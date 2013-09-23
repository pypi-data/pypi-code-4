#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-users-login',
    version='0.1.2',
    url='http://bitbucket.org/quein/django-users-login/',
    license='MIT',
    author='Geraldo Andrade',
    author_email='geraldo@geraldoandrade.com',
    description='Extension to manage users in django application.',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    download_url='https://bitbucket.org/quein/django-users-login/get/master.zip',
    zip_safe=True,
    platforms='any',
    install_requires=[
        'django==1.5.4'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    #test_suite='test_auth.suite',
)