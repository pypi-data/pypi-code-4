from distutils.core import setup

setup(
    name='iron-worker-utils',
    version='0.1.0',
    packages=['iron_worker_utils', ],
    license=open('LICENSE').read(),
    description='A collection of utilities for writing IronWorker tasks.',
    long_description=open('README.md').read(),
    author='Michael Warkentin',
    author_email='mwarkentin@gmail.com',
    url='http://mwarkentin.github.io/iron-worker-utils/',
)
