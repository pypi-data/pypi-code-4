#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="django-bootstrap-staticfiles",
    version="2.3.2.1",
    packages=find_packages(),
    package_data={
        'django_bootstrap_staticfiles': [
            'static/css/*.css',
            'static/img/*.png',
            'static/js/*.js',
        ],
    },

    # metadata for upload to PyPI
    author="George Song",
    author_email="george@55minutes.com",
    description="Django app that provides compiled Bootstrap assets",
    license="MIT",
    keywords="django app staticfiles twitter bootstrap",
    url="https://github.com/55minutes/django-bootstrap-staticfiles",
    download_url="http://pypi.python.org/pypi/django-bootstrap-staticfiles",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
    ]
)
