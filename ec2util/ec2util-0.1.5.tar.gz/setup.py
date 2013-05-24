#!/usr/bin/env python

from setuptools import setup

setup(name='ec2util', 
	description='Performs common ec2 tasks on the command line. Written in Python, based on boto.',
	version='0.1.5', 
	author='laszlocph',
    author_email='laszlo@falconsocial.com',
    url='https://github.com/laszlocph/ec2util.git',
    packages=['ec2util'],
    entry_points={
        'console_scripts': [
            'ec2util = ec2util.ec2util:main']
    },
    install_requires=['boto', 'PrettyTable', 'docopt']
)
