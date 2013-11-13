from distutils.core import setup

setup(
		name='SongsPKMP3NameCleaner',
		version='1.0',
		author='Anuj Patel',
		author_email='patelanuj28@gmail.com',
		packages=['bin'],
		scripts=['bin/convert_name.py'],
		url='http://pypi.python.org/pypi/SongsPKMP3NameCleaner/',
		license='LICENSE.txt',
		description='Useful Songs.pk filename related stuff.',
		long_description=open('README.txt').read(),
		)
