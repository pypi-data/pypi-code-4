from setuptools import setup, find_packages

setup(
	name="valhalla",
	version="0.0.4",
	description='A slim validation library with a very elegant API designed to afford the least amount of typing.',
	long_description=open('README.md').read(),
	keywords='',
	url='http://github.com/petermelias/valhalla',
	author='Peter M. Elias',
	author_email='petermelias@gmail.com',
	license='MIT',
	packages=find_packages(),
	install_requires=[],
	extras_require={
		'test': ['nose', 'coveralls']
	},
	test_suite='nose.collector',
	classifiers=[
		'Environment :: Web Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
		'Topic :: Software Development :: Libraries :: Python Modules'
	]
)