#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/emailcheck.py,v 1.2 2013/06/11 19:54:09 csoftmgr Exp $
# $Date: 2013/06/11 19:54:09 $

import Csys, os, os.path, sys, re
from Csys.DNS import dnsname, dnsip, dnsmx
from Csys.MailInternet import MailInternet, PostfixConfig

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: emailcheck.py,v 1.2 2013/06/11 19:54:09 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

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
	debug = False
	if options.verbose: #{{
		verbose = '-v'
		sys.stdout = sys.stderr
	#}
	elif debug: #{
		debug = open('/tmp/emailcheck.debug', 'w')
		sys.stdout = sys.stderr = debug
	#}
	Csys.getoptionsEnvironment(options)
	postfixConfig = PostfixConfig()
	# print postfixConfig.dumpAttrs()
	mxips = set([])
	mydestination = [
		s for s in Csys.COMMA_SPACES_NL.split(postfixConfig.mydestination) \
		if s.strip()
	]
	for dest in mydestination: #{
		for mx in dnsmx(dest, True, True): #{
			mxips |= set(mx.ip)
		#}
	#}
	from fileinput import input
	msg = MailInternet(input(args))
	outClass = Csys.CSClassDict(dict(
		sender		= msg.get('Reply-To') or msg.get('From') or msg.get('Sender'),
		errors		= [],
		ipaddrs		= None,
		postmaster	= 'postmaster@' + postfixConfig.myorigin,
		progname	= Csys.Config.progname.replace('.py', ''),
		ipaddr		= '',
		hostname	= '',
	))
	cols = outClass.__dict__
	received = msg.firstReceived(None, mxips)
	ipaddr = None
	hostname = None
	if received: #{
		ipaddr = received.ip
		if not msg.get('X-Csys-Originating-IP'): #{
			msg.replace('X-Csys-Originating-IP', ipaddr)
		#}
		hostname = dnsname(ipaddr)
		outClass.ipaddr		= ipaddr
		outClass.hostname	= hostname
	#}
	if not hostname: #{{
		outClass.errors.append('No reverse DNS for IP %s' % ipaddr)
	#}
	else: #{
		ipaddrs = dnsip(hostname, wantarray=True)
		if not ipaddr in ipaddrs: #{
			if not ipaddrs: #{{
				outClass.errors.append('No IP for %(hostname)s' %cols)
			#}
			else: #{
				outClass.ipaddrs = repr(ipaddrs)
				outClass.errors.append('ipaddr %s not in host %s IPs %s' % (
					ipaddr, hostname, outClass.ipaddrs
				))
			#}}
		#}
	#}}
	if outClass.errors: #{{
		outClass.outmsg = (
			'The following inconsistencies in DNS (Domain Name Service\n'
			'will cause email from %(ipaddr)s to be rejected by many mail\n'
			'servers as they are often an indicator of systems used to\n'
			'send unsolicited e-mail, phishing messages, and other malware.\n\n'
			'Reverse DNS (rDNS) maps IP addresses to host names.  Many ISPs,\n'
			'including AOL, will not accept mail from hosts without rDNS\n\n'
			'If a host name is returned by rDNS, a second DNS lookup checks\n'
			'the IP address(es) associated with that host name to see that\n'
			'the connecting IP, %(ipaddr)s, is assigned to that host name\n\n'
			'The following problems were found:\n\n'
		) % cols
		outClass.outmsg += '\n'.join(outClass.errors)
	#}
	else: #{
		outClass.outmsg = (
			'No DNS problems were found for:\n\t%(hostname)s [%(ipaddr)s]'
		) % cols
	#}}
	newmsg = (
		'From: %(postmaster)s\n'
		'To: %(sender)s\n'
		'Cc: %(postmaster)s\n'
		'Subject: %(progname)s results for %(hostname)s [%(ipaddr)s]\n\n'
		'%(outmsg)s\n\n'
		'Thanks\n\n'
		'%(postmaster)s\n'
	) % cols
	if verbose: #{{
		print newmsg
	#}
	else: #{
		cmd = ('%s -t' % Csys.Config.sendmail)
		if debug: #{
			print newmsg
			print cmd
			sys.stderr = debug
		#}
		sendmail = Csys.popen(cmd, 'w')
		sendmail.write(newmsg)
	#}
#}
if __name__ == '__main__': #{
	main()
#}
