# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-rforum',
    version='0.0.18',
    author=u'Oscar M. Lage Guitian',
    author_email='im@oscarmlage.com',
    packages = find_packages(),
    include_package_data = True,
    url='http://bitbucket.org/r0sk/django-rforum',
    license='BSD licence, see LICENSE file',
    description='Yet another Django Forum App',
    zip_safe=False,
    long_description=open('README.rst').read(),
    install_requires=[
        "Django < 1.5",
        "South == 0.8.1",
        "django-tinymce >= 1.5.1b2",
        "django-allauth == 0.13.0",
        "PIL == 1.1.7",
        "django-filebrowser-no-grappelli == 3.1.1",
        "django-tagging == 0.3.1",
        "django-compressor == 1.3",
        "sorl-thumbnail == 11.12",
        "django-mailer",
    ],
    dependency_links = [
        'https://github.com/pinax/django-mailer/tarball/master#egg=django-mailer',
    ],
    keywords = "django application forum board",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
