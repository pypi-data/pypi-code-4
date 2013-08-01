# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='geventhttpclient-oauthlib',
    version='0.1a',
    install_requires=[
        'geventhttpclient>=1.0a',
        'oauthlib>=0.3.0'],
    url='https://github.com/jneight/geventhttpclient-oauthlib',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    author='Javier Cordero',
    author_email='jcorderomartinez@gmail.com'
)
