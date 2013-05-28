#!/usr/bin/env python
from distutils.core import setup

setup(
    name='LewisUtils',
    version='0.0.0',
    author='Lewis Zhou',
    author_email='lewisou@gmail.com',
    packages=['lewisou.utils'],
    # scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/LewisUtils/',
    license='LICENSE.txt',
    description='Useful utils stuff.',
    long_description=open('README.txt').read(),
    install_requires=[
        # "Django >= 1.1.1",
        # "caldav == 0.1.4",
    ],
)
