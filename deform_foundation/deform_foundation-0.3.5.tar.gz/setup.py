import os

from setuptools import setup, find_packages

version = '0.3.5'

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()

setup(name="deform_foundation",
      version=version,
      install_requires=['deform > 0.9'],
      
      description="A template package for deform that uses Foundation",
      long_description=README,
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author="Parnell Springmeyer",
      author_email="ixmatus@gmail.com",
      url="http://bitbucket.org/ixmatus/deform-foundation",
      license="PSF",
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      )
