from distutils.core import setup

setup(
    name='PeeweePaginator',
    version='0.1.0',
    author='JoeDRL',
    author_email='joe.desruisseaux.langlois@gmail.com',
    packages=['peewee_paginator', 'peewee_paginator.test'],
    url='http://pypi.python.org/pypi/PeeweePaginator/',
    license='LICENSE.txt',
    description='Django-like Pagination Classes For Peewee',
    long_description=open('README.txt').read(),
    install_requires=[
        "peewee >= 2.0.0",
    ],
)