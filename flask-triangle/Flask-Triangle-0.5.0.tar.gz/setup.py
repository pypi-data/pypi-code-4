#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(

    name='Flask-Triangle',
    version='0.5.0',
    author='Morgan Delahaye-Prat',
    author_email='mdp@arjel.fr',
    description=('Integration of AngularJS and Flask.'),
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=['flask', 'jsonschema'],
    tests_require=['nose'],
    url='https://github.com/morgan-del/flask-triangle',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
