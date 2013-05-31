import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'Paste',
    'WebTest',
    'dingus',
    'objgraph']


setup(name='objgraph_middleware',
      version='0.2',
      description='Memory data logging middleware',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      license='MIT',
      author='Ignas Mikalajunas',
      author_email='ignas@uber.com',
      url='',
      keywords='web wsgi flask middleware objgraph memory profiling',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=True,
      test_suite='objgraph_middleware',
      install_requires=requires)
