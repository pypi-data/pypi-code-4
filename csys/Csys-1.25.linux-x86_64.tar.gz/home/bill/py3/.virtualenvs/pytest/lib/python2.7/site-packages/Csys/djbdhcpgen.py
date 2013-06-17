#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/djbdhcpgen.py,v 1.1 2011/10/05 19:30:44 csoftmgr Exp $
# $Date: 2011/10/05 19:30:44 $

import Csys, os, os.path, sys, re
import Csys.Netparams

__doc__ = '''Generate djbdns zone files for dhcp pool

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: djbdhcpgen.py,v 1.1 2011/10/05 19:30:44 csoftmgr Exp $
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

	dhcpConfig = os.path.join(Csys.prefix, 'etc/csadmin/dhcpd.conf')
	if not os.path.isfile(dhcpConfig): #{
		sys.stderr.write('%s missing\n' % dhcpConfig)
		sys.stderr.write('Run csadmin to configure dhcpd')
		sys.exit(1)
	#}
	cfg = Csys.ConfigParser((
		os.path.join(Csys.prefix, 'etc/csadmin/network.conf'),
		dhcpConfig
	))
	dhcpConfig = cfg.getDict('dhcpd', asClass=True)
	netwConfig = cfg.getDict('network', asClass=True)
	internalname = netwConfig.internalname
	domain = internalname.split('.', 1)[1]
	ipaddr = loaddr = Csys.Netparams.IPaddr(dhcpConfig.low_ipaddr)
	hiaddr = Csys.Netparams.IPaddr(dhcpConfig.high_ipaddr)
	print '# start dhcp range %s -> %s' % (loaddr, hiaddr)
	fmt = '=dhcp-%%03d-%s:%%s:' % domain
	while(ipaddr <= hiaddr): #{
		print fmt % (ipaddr.ipaddr[3], ipaddr)
		ipaddr = ipaddr.incrip()
	#}
	print '# end dhcp range %s -> %s' % (loaddr, hiaddr)
#}
if __name__ == '__main__': #{
	main()
#}
