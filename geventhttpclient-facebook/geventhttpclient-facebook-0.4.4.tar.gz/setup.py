#!/usr/bin/env python
from distutils.core import setup

setup(
    name='geventhttpclient-facebook',
    version='0.4.4',
    install_requires=[
	'geventhttpclient>=1.0a'],
    description='Port of the original facebook sdk <https://github.com/pythonforfacebook/facebook-sdk>'
		'to use geventhttpclient <https://github.com/gwik/geventhttpclient>'
		'This client library is designed to support the Facebook '
                'Graph API and the official Facebook JavaScript SDK, which '
                'is the canonical way to implement Facebook authentication.',
    author='Javier Cordero Martinez',
    maintainer='Javier Cordero Martinez',
    maintainer_email='jcorderomartinez@gmail.com',
    url='https://github.com/jneight/geventhttplib-facebook',
    license='Apache',
    py_modules=[
        'facebook',
    ],
    long_description=open("README.rst").read(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
)
