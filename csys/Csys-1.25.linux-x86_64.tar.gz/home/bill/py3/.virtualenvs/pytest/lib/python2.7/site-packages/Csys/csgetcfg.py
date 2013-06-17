#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/csgetcfg.py,v 1.2 2009/11/25 07:49:11 csoftmgr Exp $
# $Date: 2009/11/25 07:49:11 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Get options from INI style configuration files.

usage: %s file section option [option...]''' % Csys.Config.progname

__doc__ += '''

$Id: csgetcfg.py,v 1.2 2009/11/25 07:49:11 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

parser = Csys.getopts(__doc__)

# Add program options to parser here

parser.add_option('-a', '--all',
	action='store_true', dest='all', default=False,
	help='Get all options'
)
parser.add_option('--eval',
	action='store_true', dest='eval', default=False,
	help='Output format for eval in scripts'
)

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

cfgfile = args.pop(0)

#if not os.path.isfile(cfgfile): #{
#	sys.stderr.write(__doc__)
#	sys.stderr.write('\n%s: >%s< is is not a file\n')
#	sys.exit(1)
##}

cfg = Csys.ConfigParser(cfgfile)
# cfg.readfiles(cfgfile)
section = args.pop(0)

rec = dict(cfg.items(section))

if options.all: #{
	args = rec.keys()
	options.eval = True
#}

args.sort()

for arg in args: #{
	val = rec[arg].replace('\n', ' ').strip()
	if options.eval: print '%s=%s' % (arg, repr(val))
	else: print val
#}
