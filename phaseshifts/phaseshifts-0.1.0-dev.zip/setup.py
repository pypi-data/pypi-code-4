import os

#from setuptools import setup, find_packages
#import fix_setuptools_chmod
from numpy.distutils.core import Extension, setup

#import phaseshifts
from phaseshifts.__version__ import __version__
import sys, os

if len(sys.argv) == 1:
    sys.argv.append('install')
	
dist = setup(
        name = 'phaseshifts',
		#package_dir = {'':'phaseshifts'},
		packages = ['phaseshifts'],
        version = __version__,
        author='Liam Deacon',
        author_email='liam.m.deacon@gmail.com',
        license='MIT License',
        url='https://pypi.python.org/pypi/phaseshifts',
        description='Python-based version of the Barbieri/Van Hove phase shift calculation package for LEED/XPD modelling',
        long_description=open(os.path.join('phaseshifts','README.rst')).read() if os.path.exists(os.path.join('phaseshifts','README.rst')) else None,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Console',
			#'Environment :: X11 Applications :: Qt', #The end goal is to have Qt or other GUI frontend
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
            ],
        #packages = find_packages(),
        include_package_data = True,
        package_data = {
			# If any package contains *.txt or *.rst files, include them:
			'': ['*.txt', '*.rst'],
			'lib':['*.f', '*.c', '*.h']
			},
        #data_files = periodictable.data_files(),
        install_requires = ['scipy', 'numpy', 'periodictable'],
		ext_modules=[Extension(name='phaseshifts.libphsh', sources=[os.path.join('phaseshifts','lib','libphsh.f')])],
)

# End of file
