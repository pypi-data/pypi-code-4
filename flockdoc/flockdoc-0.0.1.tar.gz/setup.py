import os
from setuptools import setup, find_packages

import flockdoc

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:  # for tox
        return ''

setup(
    # System information
    name='flockdoc',
    version=flockdoc.__version__,
    packages=find_packages(exclude=('test',)),
    scripts=["flockdoc/bin/flockdoc"],
    zip_safe=True,
    requires=[
        'Markdown (==2.3.1)',
        'PyYAML (==3.10)',
        'Jinja2 (==2.7)',
        'Pygments (==1.6)',
    ],
    tests_require=[
        'nose==1.3.0',
    ],

    # Human information
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    url='https://github.com/brianhicks/flockdoc',
    description='Create example API documentation in multiple languages',
    long_description=read('README.md'),
    license='Apache',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
    ],
)
