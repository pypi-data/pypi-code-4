# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-enumerify',
    version='0.3.3',
    author=u'Faisal Mahmud',
    author_email='faisal@willandskill.se',
    packages=find_packages(),
    url='http://bitbucket.org/willandskill/django-enumerify',
    license='BSD licence, see LICENCE.txt',
    description='Simple Enum class instead of tuples',
    long_description=open('README.md').read(),
    zip_safe=False,
    test_suite = "testproject.runtests.runtests",
)