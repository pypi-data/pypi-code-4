
# -*- coding: utf-8 -*-

import os
import platform
import re
import sys

from distutils import dep_util
from distutils import log
from distutils.core import setup
from distutils.core import Extension
from distutils.cmd import Command
from distutils.command.build_scripts import build_scripts as _build_scripts
from distutils.command.install_scripts import install_scripts as _install_scripts



_regex_setupvarireplace_check_firstline = re.compile('^#!.*python[0-9.]*([ \t].*)?$')
_regex_setupvarireplace_detect_installpath = re.compile('^(\s*)([A-Za-z0-9_]+)\s*=.+#\s*SETUP-REPLACE:\s*INSTALL-PREFIX\s*$')
_regex_setupvarireplace_detect_librarypath = re.compile('^(\s*)sys\.path\.append\s*\(.+#\s*SETUP-REPLACE:\s*LIBRARY-PATH\s*$')
_regex_setupvarireplace_detect_inline_scan = re.compile('.+#\s*SETUP-REPLACE:\s*INLINE-SCAN\s*$')
def _setup_variable_replace(input_filepath, install_path=None, library_path=None, reverse_op=False, output_filepath=None):
	""" replace library path and installation root in specified file

	Argument:
		input_filepath - path of file to read
		install_path=None - path of installation prefix
		library_path=None - path of library
		reverse_op=False - perform reverse operation
		output_filepath=None - path to write result
	"""

	if output_filepath is None:
		output_filepath = input_filepath

	outdata = []

	fp = open(input_filepath, 'rb')
	leading = fp.readline()
	if '#!' != leading[0:2]:
		fp.close()
		return
	if (True == reverse_op) and (_regex_setupvarireplace_check_firstline.match(leading) is not None):
		if sys.executable is None:
			outdata.append("#!/usr/bin/python")
		else:
			outdata.append("#!" + sys.executable)
	else:
		outdata.append(leading.rstrip())
	for l in fp:
		codeline = None
		if codeline is None:
			m = _regex_setupvarireplace_detect_installpath.match(l)
			if m is not None:
				indent_string = m.group(1)
				varname = m.group(2)
				if not reverse_op:
					codeline = "%s%s = '%s'\t# SETUP-REPLACE: INSTALL-PREFIX" % (indent_string, varname, install_path.encode('string_escape'),)
				else:
					codeline = "%s%s = None\t# SETUP-REPLACE: INSTALL-PREFIX" % (indent_string, varname,)
		if codeline is None:
			m = _regex_setupvarireplace_detect_librarypath.match(l)
			if m is not None:
				indent_string = m.group(1)
				if not reverse_op:
					codeline = "%ssys.path.append('%s')\t# SETUP-REPLACE: LIBRARY-PATH" % (indent_string, library_path.encode('string_escape'),)
				else:
					codeline = "%ssys.path.append(None)\t# SETUP-REPLACE: LIBRARY-PATH" % (indent_string,)
		if codeline is None:
			m = _regex_setupvarireplace_detect_inline_scan.match(l)
			if m is not None:
				codeline = l.rstrip()
				if not reverse_op:
					codeline = codeline.replace('@LIBRARY_PATH@', library_path.encode('string_escape'))
					codeline = codeline.replace('@INSTALL_PATH@', install_path.encode('string_escape'))
				else:
					codeline = codeline.replace(library_path.encode('string_escape'), '@LIBRARY_PATH@')
					codeline = codeline.replace(install_path.encode('string_escape'), '@INSTALL_PATH@')	# must reverse INSTALL_PATH in last step since which is common prefix in build process
		if codeline is None:
			codeline = l.rstrip()
		outdata.append(codeline)
	fp.close()

	fp = open(output_filepath, 'wb')
	fp.write("\n".join(outdata))
	fp.write("\n")
	fp.close()
# ### def _setup_variable_replace

class adv_build_scripts(_build_scripts):
	""" 針對產生執行用指令稿檔案特化的 build_scripts 命令實作，當執行時如果檔案不存在時則找尋 .sample 檔並轉化之 """

	user_options = _build_scripts.user_options + [
			('reverse', None, "load .py to .py.sample instead of generating .py",),
	]
	boolean_options = _build_scripts.boolean_options + ['reverse', ]

	def initialize_options(self):
		_build_scripts.initialize_options(self)

		self.build_lib = None
		self.reverse = False
	# ### def initialize_options

	def finalize_options(self):
		_build_scripts.finalize_options(self)
		self.set_undefined_options('install', ('build_lib', 'build_lib'))
	# ### def finalize_options

	def run(self):
		src_scripts = self.get_source_files()
		if not src_scripts:
			return

		fake_install_path = os.path.dirname(os.path.abspath(__file__))
		fake_library_path = os.path.abspath(self.build_lib)

		for pyfile in src_scripts:
			sampfile = pyfile + ".sample"
			if False == self.reverse:
				if (not os.path.exists(pyfile)) and os.path.exists(sampfile):
					log.info("generating %s -> %s", sampfile, pyfile)
					_setup_variable_replace(sampfile, fake_install_path, fake_library_path, output_filepath=pyfile)
			else:
				if os.path.exists(sampfile) and os.path.exists(pyfile):
					log.info("reversing %s -> %s", pyfile, sampfile)
					_setup_variable_replace(pyfile, fake_install_path, fake_library_path, reverse_op=True, output_filepath=sampfile)

		if False == self.reverse:	# not doing actual build_scripts when reversing .py to .py.sample
			_build_scripts.run(self)
	# ### def run
# ### class adv_build_scripts

class adv_install_scripts(_install_scripts):
	""" 針對所安裝執行用指令稿內容調整的特化 install_scripts 命令實作 (參考自 mercurial 的 setup.py 實作) """

	def initialize_options(self):
		_install_scripts.initialize_options(self)

		self.install_lib = None
		self.install_prefix = None
	# ### def initialize_options

	def finalize_options(self):
		_install_scripts.finalize_options(self)
		self.set_undefined_options('install', ('install_lib', 'install_lib'), ('prefix', 'install_prefix'))
	# ### def finalize_options

	def run(self):
		_install_scripts.run(self)

		library_path = os.path.abspath(self.install_lib)
		install_path = os.path.abspath(self.install_prefix)

		for outfile in self.get_outputs():
			log.info("adjusting %s", outfile)
			_setup_variable_replace(outfile, install_path, library_path)
	# ### def run
# ### class adv_install_scripts



class Serve_PyDoc(Command):
	""" 啟動 PyDoc 伺服程式 """

	# Brief (40-50 characters) description of the command
	description = "start up pydoc serve"

	# List of option tuples: long name, short name (None if no short name), and help string.
	user_options = [
		('port', 'p', 'specify the listening port',),
	]

	def initialize_options(self):
		self.port = 8080
	# ### def initialize_options

	def finalize_options(self):
		self.port = int(self.port)
		if (self.port < 1024) or (self.port > 32767):
			self.port = 8080
	# ### def finalize_options

	def run(self):
		import pydoc
		def pydocserv_ready(server):
			print '> serving at: %r ...' % (server.url,)
		def pydocserv_stopped():
			print '> pydoc server stopped.'

		pydoc.serve(self.port, pydocserv_ready, pydocserv_stopped)
	# ### def run
# ### class Serve_PyDoc



setup(name='codepackager',
		version='1.02',
		url='http://code.google.com/p/codepackager',
		description='Utility for packing code to mobile storage',
		packages=['codepackager', ],
		package_dir={'': 'lib'},
		scripts=['bin/prep_codepkg.py', 'bin/recv_codepkg.py', ],
		cmdclass={'install_scripts': adv_install_scripts, 'build_scripts': adv_build_scripts,
			'serv_doc': Serve_PyDoc, },
		requires=['PyYAML (>=3.09)', ],
		install_requires=['PyYAML >= 3.09', ],
		classifiers=['Development Status :: 5 - Production/Stable',
			'Environment :: Console',
			'Intended Audience :: Developers',
			'License :: OSI Approved :: MIT License',
			'Operating System :: POSIX',
			'Programming Language :: Python :: 2.6',
			'Programming Language :: Python :: 2.7', ],
		license='MIT License',
	)



# vim: ts=4 sw=4 ai nowrap
