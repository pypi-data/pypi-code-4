#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/pflogsumm_cleanup.py,v 1.2 2009/11/25 07:52:18 csoftmgr Exp $
# $Date: 2009/11/25 07:52:18 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: pflogsumm_cleanup.py,v 1.2 2009/11/25 07:52:18 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

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

if not args: args.append(os.path.join(
	Csys.prefix, 'var/postfix/log/postfix.sum',
))

if args[0] == '-':				fh = sys.stdin
elif args[0].endswith('.gz'):	fh=Csys.popen('zcat %s' % args[0])
else:							fh = open(args[0])

header = None

suppressPrint = False

suppressHeaders = {
	re.compile(r'^message deferral detail') 	: True,
	re.compile(r'^message bounce detail')		: True,
	re.compile(r'^message reject detail')		: True,
	re.compile(r'^smtp delivery failures')		: True,
	re.compile(r'^Warnings$')					: True,
	re.compile(r'^Fatal Errors:')				: False,
	re.compile(r'^Panics:')						: False,
	re.compile(r'^Master daemon messages')		: False,
	re.compile(r'^Per-Hour Traffic Summary')	: False,
	re.compile(r'^top 10')						: False,
	re.compile(r'^Messages with no size data')	: True,
}
for line in fh: #{
	line = line.rstrip()
	if header is None: #{
		header = (
			'From: postmaster@%s\n'
			'To: postmaster@%s\n'
			'Subject: %s %s\n\n'
		) % (Csys.Config.hostname, Csys.Config.hostname, Csys.Config.hostname, line)
		print header
		print line
		continue
	#}
	for pat, val in suppressHeaders.items(): #{
		if pat.match(line): #{
			suppressPrint = val
			break
		#}
	#}
	if not suppressPrint: print line
#}
