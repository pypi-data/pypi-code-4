#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/dnsmap.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
# $Date: 2009/11/25 01:44:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Get IP to hostname map for net block

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: dnsmap.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
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
	parser.add_option('--hosts',
		action='store_true', dest='hosts', default=False,
		help='/etc/hosts format',
	)
	parser.add_option('-c', '--checkdnsip',
		action='store_true', dest='checkdnsip', default=False,
		help='/etc/hosts format',
	)
	return parser
#} setOptions

parser = setOptions()

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'
else: verbose = ''

Csys.getoptionsEnvironment(options)

import Csys.DNS
import Csys.Netparams
Netparams = Csys.Netparams.Netparams

checkdnsip = options.checkdnsip

if checkdnsip: #{
	checkdnsip = re.compile(r'^(\S+)\s+#\s+(.*)')
#}
flags = {True : '', False : 'NOMATCH' }

for network in args: #{
	net = Netparams(network)
	ipmap = Csys.DNS.mapips(net)
	keys = ipmap.keys()
	keys.sort()
	etcHosts = options.hosts
	for ip in keys: #{
		val = ipmap[ip]
		if etcHosts: #{{
			try: #{{
				ip, c, hostname = val.split()
				print '%-16s %s\t%s' % (
					ip,
					hostname,
					hostname.split('.')[0],
				)
			#}
			except: #{
				pass
			#}}
		#}
		else: #{
			if checkdnsip and isinstance(val, basestring): #{
				R = checkdnsip.match(str(val))
				if R: #{
					ipaddr, hostname = R.groups()
					ripaddr = Csys.DNS.dnsip(hostname)
					if ipaddr.strip() != str(ripaddr).strip(): #{
						if ripaddr is None: #{{
							val += ' No A record'
						else: #{
							val = '%s IP different >%s<' % (val, ripaddr)
						#}}
					#}
				#}
			#}
			print val
		#}}
	#}
#}
