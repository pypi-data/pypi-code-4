
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


PACKAGE_NAME = 'mongo_inspector'

HERE = os.path.abspath(os.path.dirname(__file__))
INIT = open(os.path.join(HERE, PACKAGE_NAME, '__init__.py')).read()
VERSION = re.search("__version__ = '([^']+)'", INIT).group(1)


setup(
    name='mongo-inspector',
    version=VERSION,
    author='Martin Maillard',
    author_email='self@martin-maillard.com',
    description='Schema extractor for MongoDB.',
    long_description=open('README.md').read(),
    keywords='mongodb',
    license=open('LICENSE').read(),
    url='http://github.com/martinmaillard/mongo-inspector',
    packages=[PACKAGE_NAME],
    package_data={'': ['LICENSE'], PACKAGE_NAME: ['js/*.js']},
    package_dir={PACKAGE_NAME: PACKAGE_NAME},
    include_package_data=True,
    install_requires=['PyMongo'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Database',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
    ],
)
