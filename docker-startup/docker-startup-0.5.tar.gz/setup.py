#!/usr/bin/env python
"""
docker-startup
==================

TODO: description

:copyright: (c) 2013 Department of Parks & Wildlife, see AUTHORS
            for more details.
:license: BSD 3-Clause, see LICENSE for more details.
"""
from setuptools import setup, find_packages

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
for m in ('multiprocessing', 'billiard'):
    try:
        __import__(m)
    except ImportError:
        pass


tests_require = [
    'nose',
]

install_requires = [
]

version = __import__('docker_startup').get_version()

setup(
    name='docker-startup',
    version=version,
    author='Tomas Krajca, Scott Percival',
    author_email=('Tomas.Krajca@dpaw.wa.gov.au, '
                  'Scott.Percival@dpaw.wa.gov.au'),
    url='https://bitbucket.org/dpaw/docker-startup',
    description=('Startup/Install scripts for docker-based VMs.'),
    packages=find_packages(exclude=['docs']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    scripts=[],
    license='BSD License',
    include_package_data=True,
    keywords="docker dockerfile startup script dpaw",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
