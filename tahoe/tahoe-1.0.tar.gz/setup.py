"""
Tahoe Framework
---------

Provides the building blocks for a RESTful Web Service
"""
from setuptools import setup

setup(
    name='tahoe',
    version="1.0",
    url='https://github.com/lunarcorp/tahoe',
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    author='Lunar Technology Corporation',
    author_email='info@ltc.io',
    description='Provides the building blocks for a RESTful Web Service',
    long_description=__doc__,
    packages=['tahoe', 'tahoe.models', 'tahoe.models.mixins'],
    zip_safe=False,
    platforms='any',
    scripts=[],
    package_data={'tahoe': ['VERSION']},
    install_requires=[
        'setuptools',
        'Flask==0.9',
        'SQLAlchemy==0.8.1',
        'Flask-SQLAlchemy',
        'Flask-Security==1.6.3',
        'py-bcrypt==0.3',
        'simplejson==3.3.0',
        'boto==2.9.5',
        'pyes==0.20.0',
        'sphinx',
        'sphinxcontrib-httpdomain',
        'python-ultramemcached==0.0.2',
        'fixture==1.4',
        'alembic==0.5.0',
        'celery==3.0.19',
        'celery-with-redis==3.0'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
