# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = (0, 1, 3)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name='yo-fabric',
    version=__versionstr__,
    description='Default fabric tasks for you python project (Simplified version of Fabricator).',
    author='Vitaliy Korobkin',
    author_email='root@digitaldemiurge.me',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    license='MIT license',
    url='https://github.com/DigitalDemiurge/yo-fabric',
    requires=['Fabric (>= 1.4)'],

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
