from setuptools import setup

setup(
	name = 'wallpyper',
	version = '0.0.6',
	author = 'https://github.com/unwitting',
	author_email = 'jackprestonuk@gmail.com',
	packages = ['wallpyper'],
	scripts = ['bin/randomiser.py'],
	url = 'https://github.com/unwitting/wallpyper',
	license = 'LICENSE.txt',
	description = 'Tiny Python module handling Linux wallpaper changes',
	long_description = open('README.txt').read(),
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: X11 Applications :: Gnome',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: Unix',
		'Programming Language :: Python',
		'Topic :: Desktop Environment :: Gnome',
		'Topic :: Software Development :: Libraries'
	],
	install_requires = []
)
