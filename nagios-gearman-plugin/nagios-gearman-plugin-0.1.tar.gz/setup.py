#!/usr/bin/env python

from distutils.core import setup

setup(name='nagios-gearman-plugin',
        version='0.1',
        description='Nagios Plugin for Gearman Metrics',
        author='William Hutson',
        author_email='wilrnh@gmail.com',
        license="MIT",
        keywords="nagios gearman plugin",
        url='https://github.com/FastSociety/nagios-gearman-plugin',
        install_requires=["argparse","nagiosplugin","gearman"],
        
        scripts=["check_gearman.py"]
)