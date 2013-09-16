from setuptools import setup, find_packages

setup(
    name='webapi',
    version='0.1',
    description="A framework to build web (json-rpc) APIs.",
    packages = ['webapi'],
    package_dir = {'webapi':'python/webapi'},
    url='https://code.google.com/p/webapi',
    license='',
    requires=['protorpc'],
    author='nate skulic',
    author_email='nate.skulic@gmail.com'
)
