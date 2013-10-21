#!/usr/bin/env python
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


version = __import__('ars').get_version()

packages = [
	'ars',
	'ars.app',
	'ars.graphics',
	'ars.lib',
	'ars.lib.pydispatch',
	'ars.lib.six',
	'ars.model',
	'ars.model.collision',
	'ars.model.contrib',
	'ars.model.geometry',
	'ars.model.physics',
	'ars.model.robot',
	'ars.model.simulator',
	'ars.utils',
]

requires = [
	'numpy',
	# 'ode',
	# 'vtk',
]

classifiers = [
	'Development Status :: 3 - Alpha',
	#'Environment :: Console', # add when visualization can be disabled
	#'Environment :: MacOS X',
	#'Environment :: Win32 (MS Windows)'
	'Environment :: X11 Applications',
	'Intended Audience :: Science/Research',
	'Intended Audience :: Developers',
	'Intended Audience :: Education',
	# the FSF refers to it as "Modified BSD License". Other names include
	# "New BSD", "revised BSD", "BSD-3", or "3-clause BSD"
	'License :: OSI Approved :: BSD License',
	#'Operating System :: MacOS :: MacOS X',
	#'Operating System :: Microsoft :: Windows',
	# TODO: what about the OS requirements of VTK and ODE?
	'Operating System :: OS Independent',
	#'Operating System :: POSIX :: Linux',
	'Programming Language :: Python',
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 2.7',
	# no Robotics topic; Simulation is under Games/Entertainment
	'Topic :: Other/Nonlisted Topic',
	'Topic :: Scientific/Engineering :: Physics',
	'Topic :: Scientific/Engineering :: Visualization',
]

setup(
	name='ARS',
	version=version,
	description='Physically-accurate robotics simulator',
	long_description=open('README.rst').read(),
	author='German Larrain-Munoz',
	author_email='glarrain@users.noreply.github.com',
	url='http://bitbucket.org/glarrain/ars',
	#download_url='',
	#platforms='any',
	license=open('LICENSE.txt').read(),
	keywords = "simulator robotics physics open-dynamics-engine vtk",
	requires=requires,
	packages=packages,
	#package_dir={}, 
	#py_modules=[''],
	#ext_modules=[]
	#libraries=[]
	#scripts=[],
	#package_data={},
	#data_files=[],
	zip_safe=False,
	classifiers=classifiers,
)
