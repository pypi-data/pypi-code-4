#-*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

CLASSIFIERS = []

setup(
    author="Laoska Guadamuz",
    author_email="lbgm2011@gmail.com",
    name='django-shop-credomatic',
    version='0.0.1',
    description='Credomatic payment backend',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.3',
        'django-crispy-forms',
    ],
    packages=find_packages(exclude=["example", "example.*"]),
    zip_safe=False
)
