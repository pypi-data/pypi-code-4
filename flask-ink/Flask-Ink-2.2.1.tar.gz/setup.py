#!/usr/env/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='Flask-Ink',
    version='2.2.1',
    url='https://github.com/diogoosorio/flask-sapo-ink',
    license='MIT',
    author='Diogo Osório',
    author_email='diogo.g.osorio@gmail.com',
    description='Easily integrate Sapo Ink\'s framework in your Flask project.',
    packages=['flask_ink'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask>=0.10.1']
)
