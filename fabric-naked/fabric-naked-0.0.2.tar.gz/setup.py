from setuptools import setup, find_packages
import sys
import os

version = '0.0.2'
long_description = open('README.rst', 'r').read().decode('utf-8')

setup(
    name='fabric-naked',
    version=version,
    description='execute your nakedo work procedure by fabric',
    long_description=long_description,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        #'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Clustering",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Systems Administration",
    ],  # Get strings from
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    #keywords='fabric deploy',
    author='Yukihiro Okada',
    author_email='callistoiv+pypi@gmail.com',
    url='https://github.com/yuokada/fabric-naked',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    #namespace_packages=['fabric','fabric.contrib', 'fabric.extensions'],
    namespace_packages=['fabric','fabric.contrib'],
    #namespace_packages=['fabric','fabric.extensions'],
    include_package_data=True,
    zip_safe=False,
    tests_require=['nose', 'mock', 'coverage'],
    install_requires=[
        # -*- Extra requirements: -*-
        'fabric',
    ],
    #entry_points={
    # 'console_scripts' : [
    # ]
    #},
)
