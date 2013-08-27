# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='django-db-defaults',
    version='0.1.1',
    description='Persist Djago model field default values to DataBase',
    long_description="",
    author='aydav',
    author_email='ayadav@joshlabs.in',
    url='https://github.com/ayadav/django-db-defaults',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.4,<1.6',
        'south>=0.8.2',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ]
)



