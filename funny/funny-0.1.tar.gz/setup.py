from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name ='funny',
		version=0.1,
		description='Demo of package',
		author='Christina',
		author_email='beemerchristina@gmail.com',
		license='MIT',
		packages=['funny'],
		scripts=['bin/fun'],
		install_requires=['cmd2',],
		zip_safe=False)
