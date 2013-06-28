
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import mongo_inspector


setup(
    name='mongo-inspector',
    version=mongo_inspector.__version__,
    author='Martin Maillard',
    author_email='self@martin-maillard.com',
    description='Schema extractor for MongoDB.',
    long_description=open('README.md').read(),
    keywords='mongodb',
    license=open('LICENSE').read(),
    url='http://github.com/morphyn/mongo-inspector',
    packages=['mongo_inspector'],
    package_data={'': ['LICENSE'], 'mongo_inspector': ['js/*.js']},
    package_dir={'mongo_inspector': 'mongo_inspector'},
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
