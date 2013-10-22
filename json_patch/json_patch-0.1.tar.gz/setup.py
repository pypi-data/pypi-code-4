from setuptools import setup

__VERSION__ = '0.1'

setup(
    name='json_patch',
    version=__VERSION__,
    packages=['json_patch'],
    description='Implementation of the json-patch spec',
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@gmail.com',
    install_requires=['json_pointer>=0.1.2']
)
