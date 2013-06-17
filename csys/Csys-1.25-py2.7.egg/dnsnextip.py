#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/dnsnextip.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
# $Date: 2009/11/25 01:44:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Get next available IP address(es) from net block

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: dnsnextip.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

	parser.add_option('-n', '--needed',
		action='store', type='int', dest='needed', default=1,
		help='Number IPs requested',
	)
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

import Csys.DNS
import Csys.Netparams

for network in args: #{
	ipmap = Csys.DNS.availableips(network, NumberRequested = options.needed)
	if options.needed == 1:
		ipmap = [ipmap]

	for ip in ipmap:
		print ip
#}
