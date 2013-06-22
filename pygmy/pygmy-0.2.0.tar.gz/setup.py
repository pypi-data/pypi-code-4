from setuptools import setup, find_packages

import pygmy


setup(
    name='pygmy',
    packages=find_packages(),
    include_package_data=True,
    version=pygmy.__version__,
    description='',
    long_description=open('README.rst').read(),
    author=pygmy.__author__,
    author_email='matt.lenc@gmail.com',
    url='https://github.com/mattack108/pygmy',
    install_requires=[
        "pygments>=1.6",
    ],
    zip_safe=False,
)
