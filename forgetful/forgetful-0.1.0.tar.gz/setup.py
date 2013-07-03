from setuptools import setup
    
import os

root_dir = os.path.dirname(__file__)
if not root_dir:
    root_dir = '.'
long_desc = open(root_dir + '/README.md').read()

setup(
    name='forgetful',
    version='0.1.0',
    description='Background queue system with no resiliancy',
    url='https://github.com/colinhowe/forgetful',
    author='Colin Howe',
    author_email='colin@colinhowe.co.uk',
    packages=['forgetful'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    license='Apache 2.0',
    long_description=long_desc,
)
