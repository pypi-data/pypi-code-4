try:
	from ez_setup import use_setuptools
	use_setuptools()
except ImportError:
	pass
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
setup(
	name = "liveconnect",
	version = "0.1.113",
	packages = ['liveconnect'],
	install_requires = ['requests'],
	py_modules= ['ez_setup'],
	package_data = {
		'' : ['*.md']
	},
	author = "Samuel Lucidi",
	author_email = "mansam@csh.rit.edu",
	description = "LiveConnect OAuth adapter for Python",
	license = "MIT",
	keywords = "liveconnect skydrive",
	url = "http://github.com/mansam/liveconnect"
)
