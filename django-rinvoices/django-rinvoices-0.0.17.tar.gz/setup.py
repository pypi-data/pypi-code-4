# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-rinvoices',
    version='0.0.17',
    author=u'Oscar M. Lage Guitian',
    author_email='r0sk10@gmail.com',
    #packages=['rinvoices'],
    packages = find_packages(),
    include_package_data = True,
    package_data = {'': ['rinvoices/templates']},
    data_files=[('javascripts', ['rinvoices/static/js/invoices.js',])],
    url='http://bitbucket.org/r0sk/django-rinvoices',
    license='BSD licence, see LICENSE file',
    description='Yet another Django Invoicing App',
    zip_safe=False,
    long_description=open('README.rst').read(),
    install_requires=[
        "Django < 1.5",
        "South == 0.7.5",
        "sorl-thumbnail == 11.12",
        "django-compressor == 1.1.2",
    ],
    keywords = "django application invoices",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
