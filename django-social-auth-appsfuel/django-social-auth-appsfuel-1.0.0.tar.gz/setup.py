#!/usr/bin/env python
"""
Django Social Auth - Appsfuel
===========================
A [django-social-auth](https://github.com/omab/django-social-auth/) module that
authenticates against [Appsfuel](http://appsfuel.com/).
"""
from setuptools import setup, find_packages

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
for m in ('multiprocessing', 'billiard'):
    try:
        __import__(m)
    except ImportError:
        pass

setup(
    name='django-social-auth-appsfuel',
    version='1.0.0',
    author='Andrea de Marco',
    author_email='andrea.demarco@buogiorno.com',
    url='https://github.com/AppsFuel/django-social-auth-appsfuel',
    description='Appsfuel backend for django-social-auth',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'django-social-auth',
    ],
    include_package_data=True,
    tests_require=[
        'django-nose',
        'coverage',
        'httpretty',
    ],
    test_suite='testrunner.run',
)
