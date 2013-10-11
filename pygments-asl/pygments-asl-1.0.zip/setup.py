from setuptools import setup, find_packages

version = '1.0'

setup(name='pygments-asl',
      version=version,
      description='Pygments lexer for ACPI source language (ASL)',
      long_description=open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
      ],
      keywords='pygments acpi asl aml',
      author='Aron Curzon',
      author_email='curzona@gmail.com',
      url='http://pypi.python.org/pypi/pygments-asl',
      license='BSD',
      py_modules=['asl'],
      zip_safe=True,
      install_requires=[
          'setuptools',
          'pygments',
      ],
      tests_require=[
          'nose',
      ],
      entry_points={
          'pygments.lexers': 'openssl=asl:AslLexer',
      },
)
