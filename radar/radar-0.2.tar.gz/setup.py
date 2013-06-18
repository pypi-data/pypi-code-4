import os
from setuptools import setup, find_packages

try:
  readme = open(os.path.join(os.path.dirname(__file__), 'readme.rst')).read()
except:
  readme = ''

version = '0.2'

setup(
    name='radar',
    version=version,
    description=("Generate a random date from range given."),
    long_description=readme,
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='random date, python',
    author='Artur Barseghyan',
    author_email='artur.barseghyan@gmail.com',
    package_dir={'':'src'},
    packages=find_packages(where='./src'),
    url='https://bitbucket.org/barseghyanartur/radar',
    license='GPL 2.0/LGPL 2.1',
    #install_requires=['python-dateutil']
)
