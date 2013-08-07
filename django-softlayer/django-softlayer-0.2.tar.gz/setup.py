### -*- coding: utf-8 -*- ####################################################
"""
Configuration file used by setuptools. It creates 'egg', install all dependencies.
"""

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#Dependencies - python eggs
install_requires = [
    'setuptools',
    'Django >= 1.4.1',
    'python-cloudfiles==1.7.10',
    'django-cumulus==1.0.5',
    'softlayer-object-storage==0.4.6',
]

#Execute function to handle setuptools functionality
setup(name="django-softlayer",
    version="0.2",
    description="Django storage for SoftLayer Cloud Storage",
    long_description=read('README'),
    author='Arpaso',
    author_email='arvid@arpaso.com',
    url='https://github.com/Arpaso/django-softlayer',
    download_url='https://github.com/Arpaso/django-softlayer/tarball/0.2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    keywords = ['django', 'softlayer', 'storage', 'cloudfiles'],
    classifiers=(
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        ),
)