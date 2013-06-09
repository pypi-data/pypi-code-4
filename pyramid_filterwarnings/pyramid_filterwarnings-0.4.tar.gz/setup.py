import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
#CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

with open(os.path.join(here, 'pyramid_filterwarnings',
                       '__init__.py')) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(v_file.read()).group(1)


setup(name='pyramid_filterwarnings',
      version=version,
      description='Configure python warnings for the Pyramid web framework',
      long_description=README,  #  + '\n\n' +  CHANGES,
      classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Pyramid',
        'License :: OSI Approved :: BSD License',
        ],
      keywords='pyramid',
      author='Guillaume Gauvrit',
      author_email='guillaume@gauvr.it',
      url='https://github.com/mardiros/pyramid_filterwarnings',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools','pyramid'],
)

