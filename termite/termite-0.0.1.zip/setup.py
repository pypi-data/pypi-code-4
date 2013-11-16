from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), 'rt') as f:
    README = f.read()

setup(name='termite',
      version='0.0.1',
      author='Jose Luis Lafuente',
      author_email='jlesquembre@gmail.com',
      description='Automates your build process',
      long_description=README,
      license='GNU General Public License v3 (GPLv3)',
      url='http://jlesquembre.github.io/termite/',
      packages=['termite'],
      include_package_data=True,

      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        ],
      keywords=['automation', 'web'],
      entry_points = {
        'console_scripts': [
            'termite = termite.cmdline:main',
            'tcli = termite.cmdline:termite_cli'
          ],
        },
      install_requires=[
                        'tornado',
                        'sarge',
                        'docopt',
                        'PyYAML',
                        'glob2',
                       ]
    )
