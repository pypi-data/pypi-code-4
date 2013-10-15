#!/usr/bin/env python

#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@lpsc.in2p3.fr
#
# Version : 1.0.0 beta (2013)
#
#############################################################################

VERSION = '1.0.0'

include_dirs = []
library_dirs = []
libraries = []

#############################################################################

import os, sys, urllib

try:
	from setuptools import setup, Extension

except ImportError:
	from distutils.core import setup, Extension

#############################################################################
# CLEANUP								    #
#############################################################################

os.system('rm -f ./tiny_xslt.so')

#############################################################################

if 'build' in sys.argv or 'install' in sys.argv:

	#####################################################################

	if not 'quick' in sys.argv:
		#############################################################
		# CLEANUP						    #
		#############################################################

		os.system('rm -fr ./build')

		#############################################################
		# TARBALLS						    #
		#############################################################

		tarballs = [
			{'base_url': 'http://xmlsoft.org/sources', 'file_name': 'libxml2-2.9.1.tar.gz', 'dir_name': 'libxml2-2.9.1'},
			{'base_url': 'http://xmlsoft.org/sources', 'file_name': 'libxslt-1.1.28.tar.gz', 'dir_name': 'libxslt-1.1.28'},
		]

		#############################################################
		# DOWNLOAD TARBALLS					    #
		#############################################################

		for tarball in tarballs:

			if os.path.isfile(tarball['file_name']) == False:
				urllib.urlretrieve('%s/%s' % (tarball['base_url'], tarball['file_name']), tarball['file_name'])

		#############################################################
		# UNPACK TARBALLS					    #
		#############################################################

		for tarball in tarballs:
			os.system('tar xzf %s' % (tarball['file_name']))

		#############################################################
		# BUILD LIBRARIES					    #
		#############################################################

		if sys.platform != 'darwin':

			if sys.maxsize > 2**32:
				CFLAGS = '-m64 -fPIC -O3'
			else:
				CFLAGS = '-m32 -O3'

		else:
			CFLAGS='-arch i386 -arch x86_64 -O3'

		for tarball in tarballs:

			os.system('export PATH=$(pwd)/build/bin:$PATH && install -d build/%s && cd build/%s && CFLAGS="%s" ../../%s/configure --prefix=$(pwd)/.. --without-python --enable-static --disable-shared && make V=1 all && make install' % (tarball['dir_name'], tarball['dir_name'], CFLAGS, tarball['dir_name']))

	#####################################################################
	# LOOKUP CFLAGS							    #
	#####################################################################

	p = os.popen("build/bin/xslt-config --cflags", "r")

	for opt in p.readline().split():

		if len(opt) > 2:

			if   opt[: 2] == '-I':
				include_dirs.append(opt[2: ])

	p.close()

	#####################################################################
	# LOOKUP LIBS							    #
	#####################################################################

	p = os.popen("build/bin/xslt-config --libs", "r")

	for opt in p.readline().split():

		if len(opt) > 2:

			if   opt[: 2] == '-L':
				library_dirs.append(opt[2: ])
			elif opt[: 2] == '-l':
				libraries.append(opt[2: ])

	p.close()

#############################################################################
# SETUP									    #
#############################################################################

tiny_xslt_extension = Extension(
	'tiny_xslt/tiny_xslt',
	['tiny_xslt/tiny_xslt.c'],
	include_dirs = include_dirs,
	library_dirs = library_dirs,
	libraries = libraries
)

#############################################################################

setup(
	name = 'tiny_xslt',
	version = VERSION,
	author = 'Jerome Odier',
	author_email = 'jerome.odier@lpsc.in2p3.fr',
	description = 'Easy XSL transformations.',
	url = 'https://bitbucket.org/jodier/tiny_xslt',
	download_url = 'https://bitbucket.org/jodier/tiny_xslt/get/v1.0.0.tar.bz2',
	license = 'CeCILL-C',
	packages = ['tiny_xslt'],
	ext_modules = [tiny_xslt_extension],
)

#############################################################################
