#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('CHANGELOG.rst').read()


setup(
    name='downyt',
    version='0.1.0',
    description='Download youtube videos of different filetypes.',
    long_description="{}\n\n{}".format(readme, history),
    author='Sebastian Vetter',
    author_email='sebastian@roadside-developer.com',
    url='https://github.com/elbaschid/downyt',
    packages=['downyt'],
    package_dir={'downyt': 'downyt'},
    include_package_data=True,
    install_requires=[
        'six',
        'purl',
        'feedparser',
        'docopt',
        'requests',
        'PyYAML',
    ],
    license="MIT",
    zip_safe=False,
    keywords='video, download, youtube',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': ['downyt = downyt.cli:main',]
    },
)
