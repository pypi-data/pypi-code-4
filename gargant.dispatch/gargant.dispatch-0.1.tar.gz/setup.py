import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='gargant.dispatch',
    version='0.1',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['gargant'],
    url='https://github.com/hirokiky/gargant.dispatch',
    license='MIT',
    author='hirokiky',
    author_email='hirokiky@gmail.com',
    description='Flexible dispatcher for WSGI Applications',
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    tests_require=['pytest'],
)
