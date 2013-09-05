from distutils.core import setup

setup(
	name = 'myKMeans',
	version = '1.0.0',
	py_modules = ['myKMeans'],
	author = 'chenliyu',
	author_email = '2572065090@qq.com',
	url = 'http://pypi.python.org/ ',
	description = 'implimention of kmeans in python,first implement a local minimum version,than use it to implement a global minimum one by choosing one of the best class to split the dataset into two classes if splitting is better',
)

