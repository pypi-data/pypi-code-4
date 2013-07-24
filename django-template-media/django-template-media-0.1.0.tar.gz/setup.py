#!/usr/bin/env python
"""
Install django-template-media using setuptools
"""

from django_template_media import __version__

with open('README.rst') as f:
    readme = f.read()

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-template-media',
    version=__version__,
    description='Simple tools to extend the django admin site',
    long_description=readme,
    author='Tim Heap',
    author_email='tim@ionata.com.au',
    url='https://bitbucket.org/tim_heap/django-template-media',

    install_requires=['Django>=1.4'],
    zip_safe=False,

    packages=find_packages(),

    include_package_data=True,
    package_data={ },

    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
