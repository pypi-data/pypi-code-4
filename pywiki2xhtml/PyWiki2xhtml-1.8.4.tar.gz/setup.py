# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "PyWiki2xhtml",
    version=__import__('PyWiki2xhtml').__version__,
    description=__import__('PyWiki2xhtml').__title__,
    long_description=open('README.rst').read(),
    author = __import__('PyWiki2xhtml').__author__,
    author_email = "sveetch AT gmail.com",
    #url='http://pypi.python.org/pypi/PyWiki2xhtml',
    license = __import__('PyWiki2xhtml').__license__,
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
    include_package_data=True,
    zip_safe=False
)