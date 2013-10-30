import os
import re
from setuptools import find_packages, setup

READMEFILE = 'README.rst'
VERSIONFILE = os.path.join('elasticmodels', '_version.py')
VERSIONREGEX = r"^__version__ = ['\"]([^'\"]*)['\"]"

def get_version():
    version_file = open(VERSIONFILE, 'rt').read()
    version = re.search(VERSIONREGEX, version_file, re.M)
    if version:
        return version.group(1)
    else:
        raise RuntimeError("Unable to find version in {0}".format(VERSIONFILE))

setup(
    name='django-elasticmodels',
    version=get_version(),
    description='A tool to map Django models to ElasticSearch mappings',
    long_description=open(READMEFILE).read(),
    url='https://bitbucket.com/jvennik/django-elasticmodels',
    author='Jos Vennik',
    author_email='josvennik@gmail.com',
    license=open('LICENSE').read(),
    packages=find_packages(),
    install_requires=[
        'pyelasticsearch>=0.6'
    ],
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
    ]
)
