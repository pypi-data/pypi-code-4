from setuptools import setup, find_packages
from os import path
import codecs
import os
import re
import sys

def read(*parts):
    file_path = path.join(path.dirname(__file__), *parts)
    return codecs.open(file_path, encoding='utf-8').read()
    
def find_variable(variable, *parts):
    version_file = read(*parts)
    version_match = re.search(r"^{0} = ['\"]([^'\"]*)['\"]".format(variable), version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError("Unable to find version string.")


README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-admin-app-names-singleton',
    version='1.0',
    packages=['django_singleton_app_name'],
    include_package_data=True,
    license='MIT',
    description='Django admin enhancer',
    long_description=README,
    url='https://github.com/pylior/django-admin-app-names-singleton',
    author=find_variable('__author__', 'django_singleton_app_name', '__init__.py'),
    author_email='lioregev@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)