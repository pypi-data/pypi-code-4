from setuptools import setup

setup(
	name = 'wallpyper',
	version = '0.0.5',
	author = 'https://github.com/unwitting',
	author_email = 'jackprestonuk@gmail.com',
	packages = ['wallpyper'],
	scripts = ['bin/randomiser.py'],
	url = 'https://github.com/unwitting/wallpyper',
	license = 'LICENSE.txt',
	description = 'Tiny Python module handling Linux wallpaper changes',
	long_description = open('README.txt').read(),
	install_requires = []
)
