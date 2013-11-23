from setuptools import setup

setup(
    name = 'mass_rename',
    version = '0.0.1',
    author = 'Enrico Carlesso',
    author_email = 'enricocarlesso@gmail.com',
    packages = ['mass_rename'],
    scripts = ['bin/mass_rename'],
    url = 'https://github.com/carlesso/mass_rename',
    license = 'LICENSE.txt',
    description = 'Files group rename tool',
    long_description = open("README.txt").read()
)
