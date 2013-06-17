#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/mapnics.py,v 1.3 2006/11/02 19:24:30 csoftmgr Exp $
# $Date: 2006/11/02 19:24:30 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: mapnics.py,v 1.3 2006/11/02 19:24:30 csoftmgr Exp $
'''

__version__='$Revision: 1.3 $'[11:-2]

parser = Csys.getopts(__doc__)

# Add program options to parser here

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

import Csys.Netparams as Net

nics = Net.getNICs()

keys = nics.keys()

keys.sort()

for key in keys: #{
	nic = nics[key]
	line = '%(iface)-7s %(hwaddr)-17s %(ipaddr)-17s %(dnsname)s' % nic.__dict__
	print line
	for alias in nic.aliases: #{
		line = '%-25s %-17s %s' % ( '', alias.ipaddr, alias.dnsname)
		print line
	#}
#}

