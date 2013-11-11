try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='keepify-py',
    version='0.1.0',
    author='the decimal',
    author_email='yaser.al3shry@gmail.com',
    packages=['keepify'],
    url='https://github.com/thedecimal/keepify-py',
    license='LICENSE.txt',
    description='Official Keepify library to track events from your Python application',
    long_description=open('README.txt').read()
)