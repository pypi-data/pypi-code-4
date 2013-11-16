from setuptools import setup, find_packages

version = '0.1'

setup(name='picasa_fetcher',
      version=version,
      description="Fetch images from Picasa",
      long_description=open('README.rst').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='jimflow picasa',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'gdata>=2.0.18'
      ],
      entry_points="""
      [console_scripts]
      picasa_fetcher = picasa_fetcher.main:run
      """,
      )
