import koality_cli
from setuptools import setup, find_packages

setup(
	name="koality_cli",
	version=koality_cli.__version__,
	description="Koality client wrapper for git and hg",
	keywords="cli, command line",
	url='https://koalitycode.com',
	author='jchu @ koality',
	author_email='jchu@koalitycode.com',
	license='Koality license and tos @ https://koalitycode.com/terms',
	packages=find_packages(exclude=[
		"tests",
	]),
	install_requires=[
		'docopt',
		'argparse',
		'pyyaml',
	],
	entry_points={
		'console_scripts': [
			'ko = koality_cli.scripts.koality:main',
		],
	},
)
