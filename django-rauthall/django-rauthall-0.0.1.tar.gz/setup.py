# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-rauthall',
    version='0.0.1',
    author=u'Oscar M. Lage Guitian',
    author_email='r0sk10@gmail.com',
    #packages=['rauthall'],
    packages = find_packages(),
    include_package_data = True,
    package_data = {'': ['rauthall/templates', 'rauthall/static','rauthall/fixtures',], 'rauthall-example': ['rauthall-example/*']},
    url='http://bitbucket.org/r0sk/django-rauthall',
    license='BSD licence, see LICENSE file',
    description='Yet another Django Auth App',
    zip_safe=False,
    long_description=open('README.rst').read(),
    install_requires=[
        "Django < 1.5",
        "South == 0.8.1",
        "django-compressor == 1.3",
        "sorl-thumbnail == 11.12",
        "django-allauth == 0.13.0",
    ],
    keywords = "django application auth",
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
