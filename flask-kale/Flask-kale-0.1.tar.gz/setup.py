# -*- coding: utf-8 -*-
"""
    flask-kale setup script

    blah blah blah

    :copyright: uniphil 2013
    :license: dwtfyw with optional coffee stipulation (one large dark black)
"""

from setuptools import setup


setup(
    name='Flask-kale',
    version='0.1',
    author='Phil Schleihauf',
    author_email='uniphil@gmail.com',
    url='https://github.com/uniphil/flask-kale',
    license='dwtfyw with optional coffee stipulation (one large dark black)',
    description='Use kale models on a flask project',
    install_requires=['flask', 'kale'],
    py_modules=['flask_kale'],
)
