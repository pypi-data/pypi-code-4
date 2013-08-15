from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name ='Mypackage',
		version=0.1,
		description='Program to create a package ',
		author='Christina',
		author_email='beemerchristina@gmail.com',
		license='MIT',
		packages=['Mypackage'],
		scripts=['bin/shell'],
		install_requires=['cmd2',],
		zip_safe=False)
