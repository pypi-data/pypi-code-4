try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from proj import __version__

setup(
    name='cdproj',
    version=__version__,
    author='Paul Ollivier',
    author_email='contact@paulollivier.fr',
    url='https://github.com/paulollivier/cdproj',
    license= "MIT",
    description='A really simple langage-independent project manager.',
    long_description=open('README.md', 'r').read(),
    requires=[],
    entry_points={
      'console_scripts': [
          'cdproj = proj:main',
          ]
      },
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
