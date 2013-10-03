"""
A Flask-based framework that handles the tedious things
"""
from setuptools import setup

setup(
    name='tahoe',
    version="1.0.3.1",
    url='http://lunarcorp.github.io/tahoe/',
    license='The MIT License: http://www.opensource.org/licenses/mit-license.php',
    author='Lunar Technology Corporation',
    author_email='info@ltc.io',
    maintainer="Clint Ecker",
    maintainer_email="clint@ltc.io",
    description='A Flask-based framework that handles the tedious things',
    long_description=__doc__,
    packages=['tahoe', 'tahoe.models', 'tahoe.models.mixins'],
    zip_safe=False,
    platforms='any',
    scripts=[],
    download_url="https://github.com/lunarcorp/tahoe",
    install_requires=[
        'setuptools',
        'Flask',
        'SQLAlchemy',
        'Flask-SQLAlchemy',
        'Flask-Security',
        'Flask-Testing',
        'py-bcrypt',
        'simplejson',
        'boto',
        'pyes',
        'sphinx',
        'sphinxcontrib-httpdomain',
        'python-ultramemcached',
        'fixture',
        'alembic',
        'celery',
        'celery-with-redis'
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
