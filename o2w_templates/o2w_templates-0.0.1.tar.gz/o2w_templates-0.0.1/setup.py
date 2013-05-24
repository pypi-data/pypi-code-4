#encoding: utf-8
from distutils.core import setup
from setuptools import find_packages

setup(
    name='o2w_templates',
    version='0.0.1',
    author='José Sánchez Moreno',
    author_email='jose@o2w.es',
    package_data = {    
        'o2w.templates': ['templates/*'],
    },

    packages=find_packages(),
    url='http://www.o2w.es/',
    license='LICENSE.txt',
    description=u'Default sane templates 500, 404, html5, sitemap.xml',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
