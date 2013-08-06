# -*- coding: utf-8 -*-


from setuptools import setup


setup(
    name='Flask-HttpCaching',
    version='0.01',
    url='http://github.com/zakzou/flask_httpcaching',
    license='MIT',
    author='zakzou',
    author_email='zakzou@live.com',
    description='flask http caching',
    long_description=__doc__,
    py_modules=['flask_httpcaching'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
