"""
flask-ypaginate
---------------

Pagination for Flask (forked from flask-paginate) using the Twitter Bootstrap
Framework.
"""
from setuptools import setup

setup(
    name='flask-ypaginate',
    version='0.1.2',
    url='https://github.com/yanhan/flask-paginate',
    license='BSD',
    author='Pang Yan Han',
    author_email='pangyanhan@gmail.com',
    description='Pagination for Flask',
    long_description=__doc__,
    namespace_packages=['flaskext'],
    packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
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
