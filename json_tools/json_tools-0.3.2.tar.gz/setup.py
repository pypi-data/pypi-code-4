#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

try:
    import pypandoc
    description = pypandoc.convert('README.md', 'rst')
except:
    description = ''


setup(
    name='json_tools',
    version='0.3.2',

    packages=['json_tools'],
    package_dir={'json_tools': 'lib'},
    install_requires=['colorama'],

    entry_points={
        'console_scripts': [
            'json = json_tools.__main__:main',
        ]
    },

    author='Vadim Semenov',
    author_email='protoss.player@gmail.com',
    url='https://bitbucket.org/vadim_semenov/json_tools',

    description='A set of tools to manipulate JSON: diff, patch, pretty-printing',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],

    keywords=['json'],

    long_description=description
)
