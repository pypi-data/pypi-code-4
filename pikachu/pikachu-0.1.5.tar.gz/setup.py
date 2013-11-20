# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = (0, 1, 5)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name='pikachu',
    version=__versionstr__,
    description='Pika helpers',
    author='Vitaliy Korobkin',
    author_email='root@digitaldemiurge.me',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    license='MIT license',
    url='https://github.com/DigitalDemiurge/pikachu',
    requires=[
        'pika (>= 0.9.13)',
        'simplejson (>=2.6.1)'
    ],

    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
