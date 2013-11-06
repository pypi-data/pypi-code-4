#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension

import sys



# This was hacked from nibabel
if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'bdist_wininst', 'install_egg_info', 'egg_info', 'easy_install',
            )).intersection(sys.argv)) > 0:
    # setup_egg imports setuptools setup, thus monkeypatching distutils. 
    from setuptools import setup

if not 'extra_setuptools_args' in globals():
    extra_setuptools_args = dict()


with open('README.txt') as file:
    long_description = file.read()


def main(**kwargs):
    setup(name="""aonetest""",
          version='0.0.04',
          description="""description""",
          author='author name',
          author_email='arghhh',
          url='nothing',
          packages=['aonetest'],
          license=['BSD'],
          # scripts=['aone/tex/weave.py',
          #          'aone/scripts/grot',
          #          'aone/scripts/unpack'],
          # cmdclass = {'build_ext': build_ext},
          # ext_modules = [ext_module],
          # classifiers=[
          #   'Development Status :: 4 - Beta',
          #   'Topic :: Text Processing :: Markup',
          #   'License :: OSI Approved :: GNU General Public License (GPL)'],
          long_description=long_description,
          **kwargs)


if __name__ == "__main__":
    main(**extra_setuptools_args)
