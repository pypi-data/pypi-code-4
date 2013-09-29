from setuptools import setup, find_packages
setup(
	name='corunner',
	version='1.0.beta',
	license="Apache License V2.0",
	platforms="linux",
	description="A utility to transport files and execute at remote in prarallel",
	author="zwsun",
	author_email="sun33170161@gmail.com",
	url="https://sourceforge.net/projects/corunner",
	
	packages= find_packages(),
	include_package_data = True,
	zip_safe = False,

	entry_points = {
		'console_scripts' : [
			'corunner-run = corunner.TaskController:main',
			'corunner-cp = corunner.FileTransporter:main'
        	],
    	},

#	scripts=["scripts/test.py"],
      )
