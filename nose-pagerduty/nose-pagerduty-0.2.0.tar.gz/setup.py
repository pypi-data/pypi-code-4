#!/usr/bin/env python

from setuptools import setup

setup(
    name='nose-pagerduty',
    install_requires=['setuptools', 'nose>=1.3.0', 'requests>=2.0.1'],
    entry_points={
        'nose.plugins.0.10': [
            'pagerduty = nose_pagerduty.NosePagerDuty:NosePagerDutyPlugin'
        ]
    },
    version='0.2.0',
    description='PagerDuty alert plugin for nose',
    long_description='Simple plugin to trigger PagerDuty alerts when one of your nose tests fail.',
    author='Luca Martinetti',
    author_email='luca@luca.io',
    url='https://github.com/lucamartinetti/nose-pagerduty',
    license='BSD',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
    keywords='test nosetests nose nosetest plugin pagerduty alert',
    packages=['nose_pagerduty'],
    package_dir={'': 'src'},
)