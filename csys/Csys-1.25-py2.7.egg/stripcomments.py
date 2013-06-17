#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/stripcomments.py,v 1.4 2005/10/02 18:18:53 csoftmgr Exp $
# $Date: 2005/10/02 18:18:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Remove comments from input

usage: [options] %s
 options:
	--nohash	# don't strip comments starting with ``#''
	-C			# strip C-style (/* ... */) comments
	--Cplusplus	# strip C++ (//.*) comments
	-a|--all	# strip all comments listed above
''' % Csys.Config.progname

__doc__ += '''

$Id: stripcomments.py,v 1.4 2005/10/02 18:18:53 csoftmgr Exp $
'''

__doc__ = Csys.detab(__doc__)

__version__='$Revision: 1.4 $'[11:-2]

parser = Csys.getopts(__doc__)

parser.add_option('--nohash',
	action="store_true", dest="nohash", default=False,
	help="Don't strip hash comments",
)
parser.add_option('-C',
	action="store_true", dest="C", default=False,
	help='strip C (/*...*/) comments',
)
parser.add_option('--Cplusplus',
	action="store_true", dest="Cplusplus", default=False,
	help='strip C++ (//.*) comments',
)
parser.add_option('--HTML',
	action="store_true", dest="HTML", default=False,
	help='strip HTML comments',
)
parser.add_option('--SQL',
	action="store_true", dest="SQL", default=False,
	help='strip SQL comments',
)
parser.add_option('-a', '--all',
	action="store_true", dest="all", default=False,
	help='strip hash, C, and Cplusplus comments'
)
# Add program options to parser here

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

sys.argv[1:] = args

input = []
import fileinput
for line in fileinput.input(): input.append(line)
print Csys.rmComments(input,
	hash = not options.nohash,
	C = options.C,
	Cplusplus = options.Cplusplus,
	HTML = options.HTML,
	SQL = options.SQL,
	all = options.all,
)
