#!/usr/local//bin/python

# $Header: /vol/cscvs/python-Csys/mounted.py,v 1.1 2007/10/06 00:12:50 csoftmgr Exp $
# $Date: 2007/10/06 00:12:50 $

import Csys, os, os.path, sys, re

__doc__ = '''Check for mounted, non-backup directories

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: mounted.py,v 1.1 2007/10/06 00:12:50 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

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

from Csys.SysUtils import mounted

print ' '.join(mounted())
