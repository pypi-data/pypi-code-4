from passkeeper import __version__
from setuptools import setup, find_packages
import sys

long_description = open('README.md').read()

extra_kwargs = {}
if sys.version_info < (2, 7):
    extra_kwargs['setup_requires'] = ['argparse>=1.2']
    extra_kwargs['install_requires'] = ['argparse>=1.2']
if sys.version_info >= (3,):
    extra_kwargs['setup_requires'] = ['setuptools']

setup(
    name="passkeeper",
    version=__version__,
    author="Gaoda",
    author_email="18363120101@163.com",
    url='https://github.com/diaohaha/passkeeper',
    description='keep your username and password',
    long_description=long_description,
    license='BSD',
    packages=find_packages(),
    package_data={'passkeeper': ['*.db']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['passkeeper = passkeeper:main']},
    platforms=['any'],
    **extra_kwargs
)
