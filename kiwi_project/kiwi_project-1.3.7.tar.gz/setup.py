# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "kiwi_project",
    version="1.3.7",
    description="Kiwi est un module Django dont le but est de gérer des pages Wiki",
    author = "Thenon David",
    author_email = "sveetch AT gmail.com",
    #url='http://pypi.python.org/pypi/kiwi_project',
    license = "GNU General Public License",
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
        'django==1.3.2',
        'PyWiki2xhtml',
        'Sveetchies'
    ],
    include_package_data=True,
    zip_safe=False
)