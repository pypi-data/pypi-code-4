#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, Extension, find_packages
import glob

madoka_cc = glob.glob('src/*.cc')
madoka_headers = glob.glob('src/*.h')
setup (
        name = 'madoka',
        version = '0.2',
        author = "Yukino Ikegami",
        author_email='yukino0131@me.com',
        url='https://github.com/ikegami-yukino/madoka-python',
        description = """Count-Min Sketch based memory-efficient key-value structure (using Madoka C++ library)""",
        long_description = open('README.rst').read() + "\n\n" + open('CHANGES.rst').read(),

        py_modules = ["madoka"],
        ext_modules = [
            Extension('_madoka',
            sources=['madoka_swig_wrap.cxx'] + madoka_cc,
            include_dirs=['src'],
            depends=madoka_headers,
            language = "c++"
            ),
        ],
        
        headers=madoka_headers,
        packages=find_packages(exclude=['test']),
        #cmdclass = {'build_ext': build_ext },

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Text Processing :: Linguistic',
            ],
        )

