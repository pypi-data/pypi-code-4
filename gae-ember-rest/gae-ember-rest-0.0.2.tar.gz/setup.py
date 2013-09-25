#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='gae-ember-rest',
    version='0.0.2',
    description='Google App Engine NDB <> Ember Data',
    author='Mitchel Kelonye',
    author_email='kelonyemitchel@gmail.com',
    url='https://github.com/kelonye/gae-ember-rest',
    packages=['gae_ember_rest',],
    package_dir = {'gae_ember_rest': 'lib'},
    license='MIT License',
    zip_safe=True
)