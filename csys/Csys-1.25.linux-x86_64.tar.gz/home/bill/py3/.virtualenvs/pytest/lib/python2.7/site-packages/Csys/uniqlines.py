#!/csrel23/bin/python

# $Header: /vol/cscvs/python-Csys/uniqlines.py,v 1.2 2009/11/25 08:00:05 csoftmgr Exp $
# $Date: 2009/11/25 08:00:05 $

import Csys, os, os.path, sys, re

__doc__ = '''Extract unique lines from input

usage: %s [file [file...]]''' % Csys.Config.progname

__doc__ += '''

$Id: uniqlines.py,v 1.2 2009/11/25 08:00:05 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

parser = Csys.getopts(__doc__)

# Add program options to parser here

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

seen = {}

import fileinput

for line in fileinput.input(): #{
	line = line.rstrip()
	if not line in seen: #{
		print line
		seen[line] = True
	#}
#}
