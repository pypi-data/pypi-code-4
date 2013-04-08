#!/usr/bin/env python
from setuptools import setup,find_packages

requirements = open('requirements.txt', 'r').readlines()

METADATA = dict(
    name='django-bigbrother',
    version='0.3.0',
    author='Anders Petersson',
    author_email='me@anderspetersson.se',
    description='Modular Dashboard for Django Projects',
    long_description='Django-Bigbrother is a reusable, modular, dashboard for Django Projects. Designed to be easy to extend.',
    url='http://github.com/anderspetersson/django-bigbrother',
    keywords='django dashboard bigbrother monitoring',
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Environment :: Web Environment',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe = False,
    packages=find_packages(),
    extra_requires={
        'system': ['psutil>=0.3']
    }
)

if __name__ == '__main__':
    setup(**METADATA)
