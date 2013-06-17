#!/usr/local//bin/python

# $Header: /vol/cscvs/python-Csys/rmopkgenv.py,v 1.2 2009/11/25 07:54:10 csoftmgr Exp $
# $Date: 2009/11/25 07:54:10 $

import Csys, os, os.path, sys, re

__doc__ = '''Clear OpenPKG instance variables from enviornment

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: rmopkgenv.py,v 1.2 2009/11/25 07:54:10 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

skipKeys = {}.fromkeys((
	'_',
	'RPM_BUILD_DIR',
	'RPM_DOC_DIR',
	'RPM_BUILD_ROOT',
	'RPM_SOURCE_DIR',
	'HOME',
	'PWD',
	'OLDPWD',
	'TMPDIR',
))

def rmopkgenv(): #{
	l_prefix = Csys.prefix
	newenv = []
	for key, val in os.environ.items(): #{
		if not key in skipKeys and val.find(l_prefix) != -1: #{
			parts = []
			for part in val.split(':'): #{
				if part.find(l_prefix) == -1: parts.append(part)
			#}
			if not parts: #{{
				del os.environ[key]
				cmd = 'unset ' + key
			#}
			else: #{
				val = os.environ[key] = ':'.join(parts)
				cmd = '%s=%s\nexport %s' % (
					key,
					repr(val),
					key
				)
			#}}
			newenv.append(cmd)
		#}
	#}
	return newenv
#} rmopkgenv

if __name__ == '__main__': #{
	# Add program options to parser here

	def setOptions(): #{
		'''Set command line options'''
		global __doc__

		parser = Csys.getopts(__doc__)

	#	parser.add_option('-d', '--directory',
	#		action='store', type='string', dest='directory', default=None,
	#		help='Change to directory before starting process',
	#	)
	#	parser.add_option('-r', '--restart',
	#		action='store_true', dest='restart', default=False,
	#		help='restart without raising mailbox flags intially',
	#	)
		return parser
	#} setOptions

	parser = setOptions()

	(options, args) = parser.parse_args()

	if options.verbose: verbose = '-v'
	else: verbose = ''

	Csys.getoptionsEnvironment(options)
	print '\n'.join(rmopkgenv())
#}

