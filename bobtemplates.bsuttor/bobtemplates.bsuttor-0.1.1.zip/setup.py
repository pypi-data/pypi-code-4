# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '0.1.1'

setup(
    name='bobtemplates.bsuttor',
    version=version,
    description="Templates by Benoît Suttor.",
    long_description=open("README.rst").read(),
    classifiers=[
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    keywords='Templates mr.bob Plone',
    author='Benoît Suttor',
    author_email='ben.suttor@gmail..com',
    url='https://github.com/bsuttor/bobtemplates.bsuttor',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bobtemplates'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'mr.bob',
    ],
    extras_require={
        'test': [
            'mr.bob',
            'unittest2',
            'scripttest',
        ]
    },
    entry_points={},
)
