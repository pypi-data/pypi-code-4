"""
Flask-mongobit
---------------

MongoBit support in Flask
"""
from setuptools import setup

setup(
    name='Flask-mongobit',
    version='0.1.2',
    url='https://github.com/lixxu/flask-mongobit',
    license='BSD',
    author='Lix Xu',
    author_email='xuzenglin@gmail.com',
    description='MongoBit support in Flask',
    long_description=__doc__,
    packages=['flask_mongobit'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'MongoBit',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
