# from distutils.core import setup
from setuptools import setup

setup(
    name='remotestatus',
    description='A Django app that checks the status (and optional processes) of remote boxes and stores their values for viewing.',
    version='0.1.1',
    author='Sean Coonce',
    author_email='cooncesean@gmail.com',
    packages=['remotestatus',],
    url='https://github.com/cooncesean/remotestatus',
    license='LICENSE.txt',
    long_description='More info can be found at: http://github.com/cooncesean/remotestatus',
    install_requires=[
        'redis>=2.7.1',          # Datastore for the status values
        'django-celery>=3.0.1',  # To run the status checks as periodic tasks
        'paramiko>=1.11.1',      # To make the remote calls to the boxes
        'django>=1.4.1',         # To make the remote calls to the boxes
    ],
)
