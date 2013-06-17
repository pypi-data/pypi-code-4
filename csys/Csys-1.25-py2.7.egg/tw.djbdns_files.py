#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/tw.djbdns_files.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
# $Date: 2009/11/25 01:44:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Create ignore files for daemontools variables.

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: tw.djbdns_files.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

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

	verbose = ''
	if options.verbose: #{
		verbose = '-v'
		sys.stdout = sys.stderr
	#}

	Csys.getoptionsEnvironment(options)

	from glob import glob

	file = os.path.join(
		Csys.prefix,
		'var/tripwire',
		os.path.splitext(Csys.Config.progname)[0],
	)
	paths = (
		('/service/*/log',				'=%s R'),
		('/service/*/supervise',		'=%s R'),
		('/service/*/root/data*',		'%s L'),
		('/service/*/root/servers/*',	'%s R'),
	)
	output = []

	for pat, fmt in paths: #{
		output.extend([fmt % os.path.realpath(p) for p in  glob(pat)])
	#}
	open(file, 'w').write('%s\n' % '\n'.join(output))
#}
