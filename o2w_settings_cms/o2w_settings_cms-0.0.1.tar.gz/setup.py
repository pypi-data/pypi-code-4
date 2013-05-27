#encoding: utf-8
from distutils.core import setup
from setuptools import find_packages

setup(
    name='o2w_settings_cms',
    version='0.0.1',
    author='José Sánchez Moreno',
    author_email='jose@o2w.es',
    package_data = {        
    },

    packages=find_packages(),
    url='http://www.o2w.es/',
    license='LICENSE.txt',
    description=u'Helper funcions',
    long_description=open('README.txt').read(),
    install_requires=[
        'django-cms',
        'djangocms-admin-style'        
    ],
)
