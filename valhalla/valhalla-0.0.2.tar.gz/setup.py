from setuptools import setup, find_packages

setup(
	name="valhalla",
	version="0.0.2",
	description='A slim validation library with a very elegant API designed to afford the least amount of typing.',
	long_description=open('README.md').read(),
	classifiers=[],
	keywords='',
	url='http://github.com/petermelias/valhalla',
	author='Peter M. Elias',
	author_email='petermelias@gmail.com',
	license='MIT',
	packages=find_packages(),
	install_requires=[],
	extras_require={
		'test': ['nose']
	},
	test_suite='nose.collector'
)