# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-fiat',
    version='0.1',
    author=u'Faisal Mahmud',
    author_email='faisal@willandskill.se',
    packages=find_packages(),
    url='http://bitbucket.org/willandskill/django-fiat',
    license='BSD licence, see LICENCE.txt',
    description='A simple django app that makes it easier to work with currencies and countries',
    long_description=open('README.md').read(),
    zip_safe=False,
    test_suite = "testproject.runtests.runtests",
)