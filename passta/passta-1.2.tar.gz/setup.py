#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='passta',
    version=__import__('passta').__version__,
    author='Martin Natano',
    author_email='natano@natano.net',
    description='simple password manager',
    url='http://github.com/natano/passta/',
    long_description='',
    license='ISC',
    keywords=['Password', 'Safe', 'Simple', 'GPG'],
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Development Status :: 5 - Production/Stable',
    ],
    entry_points={
        'console_scripts': [
            'passta = passta.cli.main:main',
        ],
    },
    install_requires=['distribute', 'docopt'],
)
