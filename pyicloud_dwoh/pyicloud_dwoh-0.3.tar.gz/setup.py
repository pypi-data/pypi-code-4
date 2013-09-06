from setuptools import setup, find_packages


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='pyicloud_dwoh',
    version='0.3',
    url='https://github.com/latestrevision/pyicloud',
    description=(
        'PyiCloud is a module which allows pythonistas to '
        'interact with iCloud webservices.  This is an unofficial '
        'fork of the official package \'pyicloud\'.'
    ),
    author='Peter Evans and Adam Coddington',
    author_email='me@adamcoddington.net',
    packages=find_packages(),
    install_requires=required
)
