#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from setuptools import setup

setup(name='fondasms',
      version='0.2',
      description='Django app to add support for FondaSMS requests.',
      long_description=("Allow any django app to handle SMS/Call requests "
                        "using the FondaSMS Android App."),
      author='yeleman',
      author_email='rgaudin@gmail.com',
      url='http://github.com/yeleman/django-fondasms',
      packages=['fondasms'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
      ]
)
