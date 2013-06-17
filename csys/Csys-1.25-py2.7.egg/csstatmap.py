#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/csstatmap.py,v 1.1 2005/10/02 18:00:23 csoftmgr Exp $
# $Date: 2005/10/02 18:00:23 $

import Csys, os, os.path, sys, re

__doc__ = '''Create pickle file per directory with stat info.

usage: [options] %s
''' % Csys.Config.progname

__doc__ += '''

$Id: csstatmap.py,v 1.1 2005/10/02 18:00:23 csoftmgr Exp $
'''

__doc__ = Csys.detab(__doc__)

__version__='$Revision: 1.1 $'[11:-2]

parser = Csys.getopts(__doc__)

# Add program options to parser here

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

import cPickle
pname = '.cs_stats'

# File names and directories to skip
skip_list = (
	'.cvsignore',
	'CVS',
	pname,
)

def mapstats(dir): #{
	'''Get stat(2) info for everything in a directory'''
	stats = {}
	for name in os.listdir(dir): #{
		if not name in skip_list: #{
			path = os.path.join(dir, name)
			stats[name] = os.stat(path)
			if os.path.isdir(path): mapstats(path)
		#}
	#}
	pfile = os.path.join(dir, pname)
	fh = open(pfile, 'w')
	cPickle.dump(stats, fh)
	fh.close()
#} mapstats

for dir in args: mapstats(dir)
