from setuptools import setup, find_packages

setup(name='Art3dUtils',
    version='0.3.6.3',
    author='Max Korinets',
    author_email='mkorinets@gmail.com',
    license='MIT',
    description='Object models for storing and utilities for processing '
                'architecture data',
    install_requires=[
        "sqlalchemy",
        'mako'
        ],
    include_package_data=True,
    packages=find_packages())