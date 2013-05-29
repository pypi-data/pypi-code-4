import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='pyawsbuckets',
    version='1.2.0',
    author='Mark Henwood',
    author_email='mark@mcbh.co.uk',
    description='Handle Amazon S3 PUT/GET/DELETE/sign interactions',
    license='MIT',
    keywords='amazon aws s3 buckets',
    url='http://pypi.python.org/pypi/pyawsbuckets',
    packages=['pyawsbuckets'],
    install_requires=['httplib2'],
    requires=['httplib2'],
    provides=['pyawsbuckets'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]
)
