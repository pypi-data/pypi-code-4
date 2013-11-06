#!/usr/bin/env python

from distutils.core import setup

setup(
  name='headhunter',
  version='0.0.1',
  description='Minimal job scheduler written with AMQP.',
  author='Jeremy Archer',
  author_email='open-source@fatlotus.com',
  url='https://www.github.com/fatlotus/headhunter.d',
  packages=['headhunter'],
  install_requires=['pika', 'pyyaml'],
)