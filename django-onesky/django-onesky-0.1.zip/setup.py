import os
from setuptools import setup, find_packages
from onesky import __version__, __description__, __author__, __email__

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-onesky',
    version=__version__,
    author=__author__,
    author_email=__email__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description=__description__,
    long_description=README,
    url='http://github.com/onesky/django-onesky/',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
    ],
)