from setuptools import setup

__VERSION__ = '0.1.2'

setup(
    name='json_pointer',
    version=__VERSION__,
    packages=['json_pointer'],
    license='Copyright Sanoma Media',
    description='Simple implementation of the json-pointer spec',
    long_description=open('./README.rst').read(),
    author='Ernst Odolphi',
    author_email='ernst.odolphi@sanomamedia.nl',
    install_requires=[]
)



