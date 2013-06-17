#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/chkrpms.py,v 1.1 2009/11/25 01:44:52 csoftmgr Exp $
# $Date: 2009/11/25 01:44:52 $

import Csys, os, os.path, sys, re

__doc__ = '''Check rpms for inconsistencies, filtering on things
like configuration files and missing items resulting from flakey
rpmtool output (e.g. Celestial's CPAN builds :-)

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: chkrpms.py,v 1.1 2009/11/25 01:44:52 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

def main(): #{
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
		parser.add_option('-b', '--binrpm',
			action="store_true", dest='binrpm', default=False,
			help="Use /bin/rpm if available"
		)
		parser.add_option('-c', '--config',
			action="store_true", default=False,
			help="List changed configuration files"
		)
		parser.add_option('-f', '--files',
			action="append", type="string",
			help="List of rpms to check"
		)
		parser.add_option('-r', '--rpmpath',
			action="store", type="string",
			default = Csys.Config.rpm,
			help="Path to RPM default = %s" % Csys.Config.rpm,
		)
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
	if options.files : #{
		for file in options.files : #{
			fh = open(file)
			args.extend([line.strip() for line in fh if line.strip()])
			fh.close()
		#}
	#}
	rpmcmd = options.binrpm and '/bin/rpm' or options.rpmpath
	if verbose: print 'rpmcmd = ', rpmcmd
	if not args: #{
		fh = os.popen('%s -qa' % rpmcmd)
		args = [line.strip() for line in fh]
		fh.close()
	#}
	args.sort()
	if verbose: print args
	l_prefix = Csys.prefix
	skipPatterns = (
		re.compile(r'\.pyc$'),
		re.compile('%s/RPM/TMP\\b' % l_prefix),
		re.compile(r'^\s*\.\.\?'),
	)
	for rpm in args : #{
		outlines = []
		fh = os.popen('%s -V %s' % ( rpmcmd, rpm ))

		for line in fh: #{
			line = line.rstrip()
			if not options.config: #{
				parts = line.split()
				if parts[1] == 'c' : continue
			#}
			for pattern in skipPatterns : #{{
				if pattern.search(line) : break
			#}
			else : #{
				# this is executed only if there's no break in the
				# patterns in the above for loop
				if rpm: #{
					if verbose: sys.stderr.write(rpm + '\n')
					outlines.append(rpm)
					rpm = None
				#}
				outlines.append('\t%s' % line)
			#}}
		#}
		if len(outlines) > 1: print '%s\n' % '\n'.join(outlines)
	#}
#}
if __name__ == '__main__': #{
	main()
#}
