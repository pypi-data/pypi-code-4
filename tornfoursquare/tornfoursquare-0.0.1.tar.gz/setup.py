from setuptools import setup

version = '0.0.1'

setup(name='tornfoursquare',
      version=version,
      description="Foursquare auth wrapper for Tornado Web",
      long_description="""\
Foursquare auth wrapper for Tornado Web""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='tornado tornadoweb foursquare',
      author='@iopeak',
      author_email='steve@stevepeak.net',
      url='https://github.com/stevepeak/tornfoursquare',
      license='Apache v2',
      packages=['tornfoursquare'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
