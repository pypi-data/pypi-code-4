import os
from distutils.core import setup
from attendly import VERSION

setup(
    name='Attendly',
    version=VERSION,
    author='Andrew Edwards',
    author_email='andrew@attendly.com',
    url='https://attendly.me/apidocs',
    packages=['attendly',],
    license='LICENSE.txt',
    long_description=open('README.rst').read(),
    install_requires='requests>=0.13.1',
)
