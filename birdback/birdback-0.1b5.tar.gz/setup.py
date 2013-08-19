# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='birdback',
    version='0.1b5',
    url='https://github.com/Birdback/python-birdback.git',
    license='mit',
    author='Jean-Philippe Serafin',
    author_email='dev@birdback.com',
    description='Birdback API client.',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'requests>=1.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
