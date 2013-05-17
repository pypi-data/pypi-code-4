import os
from setuptools import setup, find_packages

try:
    readme = open(os.path.join(os.path.dirname(__file__), 'readme.rst')).read()
except:
    readme = ''

version = '0.1'

setup(
    name='simple_timer',
    version=version,
    description=("A timer module. Makes it easy to track elapsed time."),
    long_description=readme,
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='timer',
    author='Artur Barseghyan',
    author_email='artur.barseghyan@gmail.com',
    url='https://bitbucket.org/barseghyanartur/timer',
    package_dir={'':'src'},
    packages=find_packages(where='./src'),
    license='GPL 2.0/LGPL 2.1',
)
