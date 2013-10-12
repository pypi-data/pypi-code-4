#!/usr/bin/env python

from distutils.core import setup

setup(name='nagios-rabbitmq-plugin',
        version='0.1',
        description='Nagios Plugin for RabbitMQ Metrics',
        author='William Hutson',
        author_email='wilrnh@gmail.com',
        license="MIT",
        keywords="nagios rabbitmq plugin",
        url='https://github.com/FastSociety/nagios-rabbitmq-plugin',
        install_requires=["argparse","nagiosplugin","requests"],
        
        scripts=["check_rabbitmq.py"]
)