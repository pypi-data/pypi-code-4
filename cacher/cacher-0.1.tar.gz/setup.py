from setuptools import setup
import sys

depends = ['redis']
if sys.version[0] == 2:
    depends.append('python-memcached')

setup(
    name='cacher',
    version='0.1',
    packages=['cache'],
    url='https://github.com/legoktm/cacher',
    license='MIT License',
    author='Kunal Mehta',
    author_email='legoktm@gmail.com',
    description='A simple key-value cache frontend that can be used with different backends',
    install_requires=depends,
    test_suite="tests",
)
