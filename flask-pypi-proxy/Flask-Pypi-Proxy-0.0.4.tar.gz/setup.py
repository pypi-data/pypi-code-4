#!/bin/env python

from setuptools import setup, find_packages

setup(
    name='Flask-Pypi-Proxy',
    version='0.0.4',
    description='A Pypi proxy',
    long_description=open('README.rst').read(-1),
    author='Tomas Zulberti',
    author_email='tzulberti@gmail.com',
    license='BSD',
    url='https://github.com/tzulberti/Flask-PyPi-Proxy',
    install_requires=[
        "Flask",
        "requests",
        "python-magic",
        "pygments-json",
        "pyquery"
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords='pypi flask proxy',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
