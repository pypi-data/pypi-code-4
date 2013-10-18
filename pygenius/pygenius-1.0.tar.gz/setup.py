from setuptools import setup

setup(name='pygenius',
	  version='1.0',
	  description='Python module for collecting data from rap songs.',
	  packages=['pygenius'],
	  author='Roopa Vasudevan',
	  author_email='roopa.vasudevan@gmail.com',
	  install_requires=[
	  	'beautifulsoup4==4.1.3',
	  ],
	  classifiers=['Development Status :: 4 - Beta',
	  'Intended Audience :: Developers',
	  'Intended Audience :: Education',
	  'License :: Freely Distributable',
	  'Natural Language :: English']
	)