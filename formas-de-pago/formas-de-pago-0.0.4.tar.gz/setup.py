#encoding: utf-8
from distutils.core import setup
from setuptools import find_packages

setup(
    name='formas-de-pago',
    version='0.0.4',
    author='José Sánchez Moreno',
    author_email='jose@o2w.es',
    packages=find_packages(),
    package_data = {    
        'formas_de_pago': ['templates/billing/*'],
    },

    url='http://www.o2w.es/',
    license='LICENSE.txt',
    description=u'Métodos de pago adicionales.',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
