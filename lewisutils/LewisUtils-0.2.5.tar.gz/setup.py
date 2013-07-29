#!/usr/bin/env python
from distutils.core import setup

setup(
    name='LewisUtils',
    version='0.2.5',
    author='Lewis Zhou',
    author_email='lewisou@gmail.com',
    packages=['lewisou', 
              'lewisou.utils', 
              'lewisou.utils.httpclient', 
              'lewisou.utils.mongodb', 
              'lewisou.utils.pdf'],
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
