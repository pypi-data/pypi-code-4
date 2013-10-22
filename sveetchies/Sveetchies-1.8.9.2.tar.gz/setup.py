# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "Sveetchies",
    version=__import__('Sveetchies').__version__,
    description=__import__('Sveetchies').__doc__,
    long_description=open('README.rst').read(),
    license = "GNU General Public License (Version 2)",
    author = "Thenon David",
    author_email = "sveetch AT gmail.com",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 7 - Inactive',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'PyWiki2xhtml',
        'django>=1.3.2',
    ],
    include_package_data=True,
    zip_safe=False
)