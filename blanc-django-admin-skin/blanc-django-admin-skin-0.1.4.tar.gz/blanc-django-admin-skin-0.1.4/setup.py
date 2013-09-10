#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='blanc-django-admin-skin',
    version='0.1.4',
    description='Blanc Admin Skin for Django',
    long_description=open('README.rst').read(),
    url='http://www.blanctools.com/',
    maintainer='Steve Hawkes',
    maintainer_email='steve@hawkz.com',
    platforms=['any'],
    packages=[
        'blanc_django_admin_skin',
    ],
    package_data={'blanc_django_admin_skin': [
        'static/admin/css/*',
        'static/admin/img/*.png',
        'static/admin/img/assets/*',
        'static/admin/img/blanc/*',
        'templates/admin/base_site.html',
    ]},
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    license='BSD-2',
)
