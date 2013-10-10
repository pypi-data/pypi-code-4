from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, Extension

module1 = Extension('yakc',
                    include_dirs = ['/opt/local/include'],
                    library_dirs = ['/opt/local/lib'],
                    libraries = ['kyotocabinet'],
                    sources = ['yakc.cpp'])

setup (name = 'yakc',
       version = '0.1',
       description = 'Yet Another Kyoto Cabinet Binding',
       author = 'OKAMURA Yasunobu',
       author_email = 'okamura@informationsea.info',
       ext_modules = [module1],
       test_suite = 'yakctest',
       url = 'https://github.com/informationsea/Yet-Another-Kyoto-Cabinet-Python-Binding')
