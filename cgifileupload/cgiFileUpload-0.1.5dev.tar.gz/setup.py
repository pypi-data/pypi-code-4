from setuptools import setup, find_packages
import sys, os

_version = (0, 1, 5)
version = '%d.%d.%d' % _version

pth = os.path.abspath(os.path.dirname(__file__))
readme_file = open(os.path.join(pth, 'README.rst')).read()

setup(name='cgiFileUpload',
      version=version,
      description="file import via CGI",
      long_description=readme_file,
      keywords='',
      author='Robert Sudwarts',
      author_email='robert.sudwarts@gmail.com',
      url='https://bitbucket.org/RobertSudwarts/cgi_file_upload/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "Pillow>=2.0.0",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Utilities",
        ], 
      )
