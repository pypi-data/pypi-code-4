#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'cachefly',
    'django_cachefly',
]

requires = [
    'requests>=1.0.0,<2.0.0',
]

tests_require = [
    'nose',
    'rednose',
    'pep8',
]

setup(
    name='cachefly',
    version='1.0.0',
    description='Convenient CacheFly CDN management for Python',
    author='Nick Bruun',
    author_email='nick@bruun.co',
    url='http://bruun.co/',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={
        'cachefly': 'cachefly',
        'django_cachefly': 'django_cachefly',
    },
    include_package_data=True,
    tests_require=tests_require,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=True,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
