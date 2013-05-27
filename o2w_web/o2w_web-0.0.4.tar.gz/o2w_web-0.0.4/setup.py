#encoding: utf-8
from distutils.core import setup
from setuptools import find_packages

setup(
    name='o2w_web',
    version='0.0.4',
    author='José Sánchez Moreno',
    author_email='jose@o2w.es',
    packages=find_packages(),
    url='http://www.o2w.es/',
    license='LICENSE.txt',
    description=u'Base package for web creation',
    long_description=open('README.txt').read(),
    install_requires=[
        'django',
        'django-annoying',
        'django-pipeline',
        'cssmin',
        'slimit',
        'django-modeltranslation',
        'easy-thumbnails',
        'image-diet',
        'django-extensions',
        'django-grappelli',
        'django-rosetta',
        'django-filebrowser',
        'grappelli-modeltranslation',
        'django-pure-pagination',
        'raven',
        'o2w-cache-invalidator',
        'o2w-templates',
        'o2w-core',
        'o2w-settings'
    ],
)
