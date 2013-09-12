# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-rgallery',
    version='0.0.2',
    author=u'Oscar M. Lage Guitian',
    author_email='r0sk10@gmail.com',
    #packages=['rgallery'],
    packages = find_packages(),
    include_package_data = True,
    package_data = {'': ['rgallery/templates', 'rgallery/static','rgallery/fixtures',], 'rgallery-example': ['rgallery-example/*']},
    url='http://bitbucket.org/r0sk/django-rgallery',
    license='BSD licence, see LICENSE file',
    description='Yet another Django Gallery App',
    zip_safe=False,
    long_description=open('README.rst').read(),
    install_requires=[
        "Django < 1.5",
        "South == 0.7.5",
        "PIL == 1.1.7",
        "sorl-thumbnail == 11.12",
        "django-compressor == 1.1.2",
        "dropbox==1.5.1",
        "hachoir-core==1.3.3",
        "hachoir-metadata==1.3.3",
        "hachoir-parser==1.3.4",

    ],
    keywords = "django application gallery",
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
