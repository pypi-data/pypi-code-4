try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Yelpy',
    version='0.2.2dev',
    description='Yelp API Client',
    author='Bryan Marty',
    author_email='hello@bryanmarty.com',
    url='http://www.bryanmarty.com',
    packages=['yelpy'],
    license='GPLv2',
    install_requires=['oauth2'],
)
