import os
from setuptools import setup, Extension

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='curses_ex',
      version='0.3',
      description='Provide additional curses functions.',
      author='Atsuo Ishimoto',
      author_email='ishimoto@gembook.org',
      url='https://github.com/atsuoishimoto/python.curses_ex',
      long_description=read('README.rst'),
      classifiers=[
            "Programming Language :: Python :: 3",
            "Development Status :: 3 - Alpha",
            "Topic :: Software Development :: Libraries",
            "Environment :: Console :: Curses",
            "License :: OSI Approved :: BSD License", ],
    
      ext_modules=[
          Extension('curses_ex', ['curses_ex.c'],
               libraries = ['curses']),],
)
