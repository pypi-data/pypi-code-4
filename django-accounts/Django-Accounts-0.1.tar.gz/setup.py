from setuptools import setup, find_packages

with open('requirements.txt') as reqfile:
	requirements = reqfile.read().splitlines()

setup(
	name='Django-Accounts',
	author='Binary Birch Tree',
	author_email='binarybirchtree@users.noreply.github.com',
	url='https://github.com/binarybirchtree/django-accounts',
	download_url='https://github.com/binarybirchtree/django-accounts/archive/master.zip',
	version='0.1',
	license='GNU General Public License version 3',
	description='A batteries-included solution for Django accounts.',
	long_description=open('README.rst').read(),
	packages=find_packages(),
	include_package_data=True,
	install_requires=requirements,
	classifiers=[
		'Programming Language :: Python',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: OS Independent',
		'Framework :: Django',
		'Environment :: Web Environment',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
)
