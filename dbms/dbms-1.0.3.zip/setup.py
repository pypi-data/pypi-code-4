from setuptools import setup

setup(name='dbms',
	version='1.0.3',
	description='DataBases Made Simpler',
	long_description=''''DBMS is a database abstraction to make it easier to 
	connect and work with a variety of DB API 2 databases adapters in Python. 
	It provides dictionary type cursors, uniform connection syntax and database 
	introspection across all supported databases including Oracle, MySQL, 
	PostgreSQL, MS SQL Server and SQLite''',
	url='https://sourceforge.net/projects/pydbms/',
	keywords='database rdbms Oracle PostgreSQL MySQL SQLServer',
	classifiers=['Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Intended Audience :: Developers',
		'Topic :: Database',
		'Topic :: Database :: Database Engines/Servers'
	],
	author='Scott Bailey',
	author_email='scottrbailey@gmail.com',
	license='MIT',
	packages=['dbms'],
	zip_safe=False)
	