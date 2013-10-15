#!/usr/bin/env python

from distutils.core import setup

setup(name='nagios-filecount-plugin',
        version='0.1',
        description='Nagios Plugin for checking file counts',
        author='William Hutson',
        author_email='wilrnh@gmail.com',
        license="MIT",
        keywords="nagios file count plugin",
        url='https://github.com/FastSociety/nagios-filecount-plugin',
        install_requires=["argparse","nagiosplugin"],
        
        scripts=["check_filecount.py"]
)