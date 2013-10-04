#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pybuilder',
          version = '0.9.12',
          description = 'An extensible, easy to use continuous build tool for Python',
          long_description = '''PyBuilder is a continuous build tool for multiple languages.

PyBuilder primarily targets Python projects but due to its extensible
nature it can be used for other languages as well.

PyBuilder features a powerful yet easy to use plugin mechanism which
allows programmers to extend the tool in an unlimited way.
''',
          author = "Alexander Metzner, Michael Gruber, Udo Juettner",
          author_email = "alexander.metzner@gmail.com, aelgru@gmail.com, udo.juettner@gmail.com",
          license = 'Apache License',
          url = 'http://pybuilder.github.com',
          scripts = ['pyb'],
          packages = ['pybuilder', 'pythonbuilder', 'pybuilder.plugins', 'pybuilder.plugins.python'],
          classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: Implementation :: CPython', 'Programming Language :: Python :: Implementation :: PyPy', 'Programming Language :: Python :: 2.6', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.2', 'Programming Language :: Python :: 3.3', 'Development Status :: 3 - Alpha', 'Environment :: Console', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Topic :: Software Development :: Build Tools', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
          
          
          
          
          zip_safe=True
    )
