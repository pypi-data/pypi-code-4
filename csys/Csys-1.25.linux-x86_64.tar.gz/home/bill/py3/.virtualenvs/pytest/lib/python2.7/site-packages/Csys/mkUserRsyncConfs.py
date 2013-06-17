#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/mkUserRsyncConfs.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
# $Date: 2009/11/25 01:44:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Utility to create rsyncd.conf entries for users

usage: %s [username]''' % Csys.Config.progname

__doc__ += '''

$Id: mkUserRsyncConfs.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

allowedCidrs = ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12']

rsyncFmt = ('''
[%(user)s_upd]
	uid = %(user)s
	gid = %(gid)s
	read only = false
	# use chroot = false
	path = %(home)s
	comment = %(home)s
	hosts allow = %(cidrblocks)s
	hosts deny = *
	list = no
''').lstrip()

if __name__ == '__main__': #{
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
	from Csys.Passwd import read_passwd_shadow
	import Csys.Admin.network
	import grp
	netcfg = Csys.Admin.network.Config()
	accts = read_passwd_shadow().accts
	users = [ pw.user for pw in accts.values() if not pw.is_admin]
	if not args: args = users
	args.sort()
	if not netcfg.publiccidr in allowedCidrs: #{
		allowedCidrs.insert(0, netcfg.publiccidr)
	#}
	cidrblocks = ', '.join(allowedCidrs)
	rsyncConfigs = {} # keyed on home directory

	for user in args: #{
		pw = accts[user]
		home = pw.home
		if not home in rsyncConfigs: #{
			rsyncConfigs[home] = True
			pw.cidrblocks = cidrblocks
			pw.__dict__['gid'] = grp.getgrgid(pw.gid)[0]
			print rsyncFmt % pw.__dict__
		#}
	#}
#}
