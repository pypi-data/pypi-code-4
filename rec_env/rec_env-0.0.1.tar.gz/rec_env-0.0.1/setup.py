from setuptools import setup, find_packages, Command
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

version = "0.0.1"

install_requires = [
    'PyYAML'
]


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(name='rec_env',
      version=version,
      description="",
      long_description=README + '\n\n' + NEWS,
      classifiers=[
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      ],
      author='Luiz Irber',
      author_email='luiz.irber@gmail.com',
      license='PSF',
      packages=find_packages('rec_env'),
      package_dir={'': 'rec_env'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      cmdclass={'test': PyTest},
      platforms='any',
      )
