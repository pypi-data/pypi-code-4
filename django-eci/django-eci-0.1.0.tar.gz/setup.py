from distutils.core import setup
from setuptools import find_packages


setup(
    name='django-eci',
    version='0.1.0',
    author='Sasha Matijasic',
    author_email='sasha@selectnull.com',
    packages=find_packages(),
    url='http://ciin.eu/',
    license='LICENSE',
    description="European Citizen's Initiative",
    long_description=open('README').read(),
    install_requires=['django'],
)
