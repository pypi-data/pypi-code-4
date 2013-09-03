#!/usr/bin/env python
#coding:utf-8
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
execfile('workertier/version.py') # Load version

setup(
    name='workertier',
    version=__version__,
    description='A Scalr tutorial: Web frontend + Memcached + RabbitMQ',
    author='Thomas Orozco',
    author_email='thomas@scalr.com',
    url='https://github.com/scalr/tutorial-workertier',
    packages=[
        'workertier', 'workertier.backends', 'workertier.backends.cache', 'workertier.backends.dispatcher'
    ],
    package_dir={'workertier': 'workertier'},
    include_package_data=True,
    install_requires=["gevent", "pymemcache >= 1.1.0", "haigha", "python-daemon", "lockfile"],
    license="Apache 2",
    entry_points={
        'console_scripts': [
            'workertier = workertier.cli:cli',
        ],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
