#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pyupyun',
    version='0.1.3',
    description='Feature complete upyun REST client',
    long_description=open('README.rst').read(),
    author='Kane Dou',
    author_email='douqilong@gmail.com',
    url='https://github.com/kols/upyun',
    packages=['upyun'],
    package_data={'': ['LICENSE']},
    package_dir={'upyun': 'upyun'},
    include_package_data=True,
    install_requires=['requests'],
    license=open('LICENSE').read(),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
