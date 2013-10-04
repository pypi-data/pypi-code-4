# coding=utf-8
from setuptools import setup, find_packages


setup(
    name='dalga',
    version='0.1.0',
    author=u'Cenk Altı',
    author_email='cenkalti@gmail.com',
    url='http://github.com/cenkalti/python-dalga',
    packages=find_packages(),
    install_requires=['requests'],
    description='Dalga client in Python',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Object Brokering',
        'Topic :: System :: Distributed Computing',
    ],
)
