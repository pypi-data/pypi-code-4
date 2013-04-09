# coding=utf-8
"""
vcssshd-lib
-------------

vcssshd-lib is library for easy and fast creation of an ssh demon for popular VCSs (Mercurial and Git).
This library uses Twisted framework."""
from setuptools import setup


setup(
    name='vcssshd',
    version='0.2.0',
    url='https://bitbucket.org/ellersseer/vcssshd-lib',
    license='BSD',
    author='Dmitry Zhiltsov',
    author_email='dzhiltsov@me.com',
    description='Library for easy and fast creation of an ssh demon for popular VCSs (Mercurial and Git)',
    long_description=__doc__,
    py_modules=['vcssshd'],
    # packages=['vcssshd'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Twisted', 'pycrypto', 'pyasn1'
    ],
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Framework :: Twisted',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
