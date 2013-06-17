#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/whlserver.py,v 1.2 2009/11/25 08:01:49 csoftmgr Exp $
# $Date: 2009/11/25 08:01:49 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: whlserver.py,v 1.2 2009/11/25 08:01:49 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

	cfgfile = os.path.join(Csys.prefix, 'etc/postfix/whlserver.conf'),
	parser.add_option('-c', '--config',
		action='store', type='string', dest='config',
		default=cfgfile,
		help='Configuration File (default %s)' %cfgfile,
	)
	parser.add_option('-i', '--install',
		action='store', type='string', dest='install',
		default=None,
		help='Install in Directory for daemon tools',
	)
	parser.add_option('-l', '--loguser',
		action='store', type='string', dest='loguser',
		default='csoftmgr',
		help='Log user for daemon tools',
	)
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

def install(dir, user): #{
	'''Install program for daemon tools'''
	if os.path.exists(dir): #{
		sys.stdout = sys.stderr
		print '%s: install directory >%s< exists' % (
			Csys.Config.progname, dir
		)
		sys.exit(1)
	#}
	from pwd import getpwnam
	pw = getpwnam(user)
	print pw.pw_uid, pw.pw_gid
	logdir = os.path.join(dir, 'log')
	logdirmain = os.path.join(logdir, 'main')
	rootdir = os.path.join(dir, 'root')
	print logdir
	print logdirmain
	chmod = os.path.join(Csys.prefix, 'bin/gchmod')
	chown = os.path.join(Csys.prefix, 'bin/gchown')
	commands = (
		'%s -R %s: %s' % (chown, user, logdirmain),
		# '%s +x %s' % (chmod, runfile)
	)
	print chmod
	print chown
	Csys.mkpath(dir, mode=03755)
	Csys.mkpath(logdirmain, mode=02755)
	Csys.mkpath(rootdir, mode=02755)
	for cmd in commands: Csys.system(cmd)
	progname = os.path.join(Csys.Config.dirname, Csys.Config.progname)
	cfgfile = os.path.join(rootdir, 'whlserver.conf')
	runfile	= os.path.join(dir, 'run')
	fout = Csys.openOut(runfile, mode = 0755)
	fout.write(
		'#!/bin/sh\n'
		'exec 2>&1\n'
		'exec %s -v -c %s\n' % (progname, cfgfile)
	)
	fout.close()
	fout = Csys.openOut(cfgfile)
	fout.write(
		'[whlserver]\n'
		'host     = 127.0.0.1\n'
		'port     = 50007\n'
		'rblnames = whl.celestial.net\n'
	)
	fout.close()
	logrunfile = os.path.join(logdir, 'run')
	fout = Csys.openOut(logrunfile, mode=0755)
	fout.write(
		'#!/bin/sh\n'
		'exec setuidgid %s multilog t ./main\n' % user
	)
	fout.close()
#} install

if options.install: #{
	install(options.install, options.loguser)
	sys.exit(0)
#}

# Echo server program
import socket
import SocketServer
from Csys.DNS import inrbl
from Csys.DNS import dnsip

HOST = ''                 # Symbolic name meaning the local host
PORT = 50007              # Arbitrary non-privileged port
rblname = 'whl.celestial.net.'

cfg = Csys.ConfigParser(options.config).getDict('whlserver')

rblnames =  Csys.COMMA_SPACES.sub(' ', cfg['rblnames']).split()
if verbose: print rblnames

ipaddrPattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

class WHLRequestHandler(SocketServer.StreamRequestHandler): #{
	def handle(self): #{
		print 'in handle'
		ipaddrs = {}
		count = 0
		cached = 0
		while True: #{
			data = self.rfile.readline()
			if not data: break
			count += 1
			data = data[:-1]
			ipaddr = data.replace('get ', '')
			badfmt = False
			reply = ipaddrs.get(ipaddr)
			if reply is None: #{{
				if not ipaddrPattern.match(ipaddr): #{
					badfmt = ipaddr
					try: ipaddr = dnsip(ipaddr)
					except: ipaddr = None
					if not ipaddr: reply = ipaddrs[badfmt] = '500 None'
				#}
				if ipaddr: #{
					for rblname in rblnames: #{{
						if inrbl(ipaddr, rblname): #{
							reply = '200 OK'
							break
						#}
					#}
					else: #{
						reply = '500 None'
					#}}
					ipaddrs[ipaddr] = reply
					if badfmt: ipaddrs[badfmt] = reply
				#}
			#}
			else: #{
				cached += 1
			#}}
			print '%s -> %s' % (data, reply)
			self.wfile.write('%s\n' % reply)
		#}
		print 'processed %d requests %d cache hits' % (count, cached)
	#} handle
#} class WHLRequestHandler

Server = SocketServer.TCPServer
Server = SocketServer.ForkingTCPServer
Server = SocketServer.ThreadingTCPServer

class WHLServer(Server): #{
	def __init__(self, host, port): #{
		Server.__init__(
			self, (host, int(port)), WHLRequestHandler
		)
	#}
#} class WHLServer

server = WHLServer(cfg.get('host', ''), cfg['port'])
server.serve_forever()
sys.exit(0)
