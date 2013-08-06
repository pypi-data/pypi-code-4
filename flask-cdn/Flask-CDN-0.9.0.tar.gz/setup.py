"""
Flask-CDN
---------

Seamlessly serve your static files from a CDN.
"""
from setuptools import setup


setup(
    name='Flask-CDN',
    version='0.9.0',
    url='https://github.com/wichitacode/flask-cdn',
    license='MIT',
    author='William Fagan',
    author_email='will@wichitacode.com',
    description='Seamlessly serve the app\'s static files from a CDN',
    long_description=__doc__,
    py_modules=['flask_cdn'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    test_suite="tests",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
