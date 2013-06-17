#!/csoft/bin/python
# $Header: /vol/cscvs/python-Csys/Netparams.py,v 1.10 2013/06/11 19:51:21 csoftmgr Exp $
# $Date: 2013/06/11 19:51:21 $
# @(#) $Id: Netparams.py,v 1.10 2013/06/11 19:51:21 csoftmgr Exp $
#

import os, re, Csys, sys
from socket import *

from Csys.DNS import dnsname, ip_sort

do_dnsname = True

def set_do_dnsname(opt): #{
	global do_dnsname
	do_dnsname = opt
#} set_do_dnsname

# map netmask value to number of bits
_mask2bits = {
	'255'	: 8,
	'254'	: 7,
	'252'	: 6,
	'248'	: 5,
	'240'	: 4,
	'224'	: 3,
	'192'	: 2,
	'128'	: 1,
	'0'		: 0,
}
_re_cidr	= re.compile(r'^(?P<network>[^/]*)/(?P<bits>\d+)$')
_re_netmask	= re.compile(r"^(?P<network>.*)/(?P<mask>\d+\.\d+\.\d+\.\d+)$")
_re_dotent	= re.compile(r"(?P<ip>[\d\.]*)\.$")

def _a2b(str): #{
	'''Convert ipv4 to long'''
	bits = 0L
	# split into integer array no larger than 255
	octets = [ (int(i) & 255) for i in str.split('.') ]
	# build bits by shifting left for each octet
	for octet in octets:
		bits = (bits << 8) | octet
	# Now shift left if there weren't 4 octets
	for i in range(len(octets), 4):
		bits = bits << 8
	return bits
#} _a2b

# Some useful constants
_allones	= _a2b('255.255.255.255')
_b_one	= _a2b('0.0.0.1')

def _b2a(bits=0L): #{
	'''convert long to ipv4 string'''
	ipv4 = []
	for i in range(4):
		octet = int(bits & 255)
		bits = bits >> 8
		ipv4.append(octet)
	ipv4.reverse()
	return '%d.%d.%d.%d' % tuple(ipv4)
#} _b2a

class IPaddr(object): #{
	'''IPv4 Address for comparison and calculation purposes'''
	def __init__(self, ip='0.0.0.0'): #{
		'''String will be converted to a tuple'''
		self.ip		= ip = str(ip)
		self.ipstrt	= ipstrt = tuple(ip.split('.'))
		self.ipaddr = tuple(map(int, ipstrt))
	#} __init__

	def __cmp__(self, other): #{
		if not hasattr(other, 'ipaddr'): other = IPaddr(other)
		return cmp(self.ipaddr, other.ipaddr)
	#} __cmp__

	def __len__(self): return 16

	def __str__(self): #{
		'''Return original string that created the IP'''
		return self.ip
	#} __str__
	
	def ip2inaddr(self): #{
		'''Return PTR name for rDNS'''
		if not 'inaddr' in self.__dict__:
			octets = list(self.ipaddr)
			octets.reverse()
			self.inaddr = '%d.%d.%d.%d.in-addr.arpa.' % tuple(octets)
		return self.inaddr
	#} ip2inaddr

	def ip2long(self): #{
		'''Convert IP to long int suitable for arithmatic'''
		if not 'long' in self.__dict__: #{
			result = 0L
			# print self.ipaddr
			for octet in self.ipaddr: #{
				result = (result * 256) + octet
				# print 'result: ', result, octet
			#}
			self.long = result
		#}
		return self.long
	#} ip2long

	def long2ip(self, ip=None): #{
		'''Convert long int to IP'''
		# print 'long2ip(%d)' % ip
		iplong = long(ip)
		octets = []
		if ip is None and 'long' in self.__dict__: #{
			iplong = self.long
		#}
		# print 'ip: ', ip, iplong
		for i in range(4): #{
			rem = iplong % 256
			iplong = iplong / 256
			octets.append('%d' % rem)
			# print 'octets: ', octets
		#}
		octets.reverse()
		return(IPaddr('.'.join(octets)))
	#} long2ip

	def incrip(self, increment=1): #{
		'''Increment IP address'''
		# print 'incrip(%d)' % increment
		octets = list(self.ipaddr)
		octets[-1] += increment
		# print 'octets: ', octets
		for i in range(len(octets) - 1, 0, -1): #{
			octet = octets[i]
			# print 'octet: ', octet
			if octet > 255: #{{
				octets[i] = octet % 255
				if i > 0: octets[i-1] += octet / 255
			#}
			elif octet < 0: #{
				octets[i] = octet % 255
				if i > 0: octets[i-1] += octet / 255
			#}}
			# print 'i, octets', i, octets
		#}
		result = IPaddr('%s' % ('.'.join([str(s) for s in octets])))
		return result
	#} incrip

	def ipcmp(self, ip): #{
		'''Numeric comparison of two IPs'''
		for i in range(4):
			cmp = self.ipaddr[i] - ip.ipaddr[i]
			if cmp: return cmp
		return 0
	#} ipcmp
#} class IPaddr

class Netparams(object): #{
	def __init__(self, network, **kwargs): #{
		'''Initialize Netparams'''
		cols = self.__dict__
		self.network = network
		if kwargs:
			cols.update(kwargs)

		if not self.network:
			self.network = '0.0.0.0'
		# This matches CIDR 192.168.0.0/24
		# print 'network = %s ' % self.network
		result = _re_cidr.search(self.network)
		# print result
		if result: #{{
			self.network	= self.ipaddr = result.group('network')
			self.bits		= int(result.group('bits'))
			# print self.network, self.bits
		#}
		else: #{
			result = _re_netmask.search(self.network)
			if result: #{{
				self.network	= self.ipaddr = result.group('network')
				self.netmask	= result.group('mask')
			#}
			else: #{
				result = _re_dotent.search(self.network)
				if result: #{{
					ip_parts = result.group('ip').split('.')
					mask_parts = []
					for octet in ip_parts: #{
						mask_parts.append('255')
					#}
					for i in range(len(ip_parts), 4): #{
						ip_parts.append('0')
						mask_parts.append('0')
					#}
					self.network = self.ipaddr = '.'.join(ip_parts)
					self.netmask = '.'.join(mask_parts)
				#}
				else: #{
					self.ipaddr = self.network
				#}}
			#}}
		#}}
		if self.network == '0.0.0.0' or self.network == 'ALL': #{{
			self.network	= self.ipaddr = self.netmask = '0.0.0.0'
			self.bits		= 0
			self.hosts		= 0
		#}
		else: #{
			if not ('bits' in cols or 'netmask' in cols): #{
				self.bits = 32
				self.netmask = '255.255.255.255'
			#}
			hasbits = 'bits' in cols
			hasmask = 'netmask' in cols
			# print 'hasbits %d ' % hasbits
			# print 'hasmask %d ' % hasmask
			# print cols
			if hasbits and not hasmask: #{{
				mask_parts = ['255' for i in range(self.bits // 8)]
				# print 'mask_parts: ', mask_parts
				
				if len(mask_parts) < 4: #{
					rem = 0
					for i in range(self.bits % 8): #{
						# print 'trying'
						rem += 2**(7 - i)
					#}
					mask_parts.append('%d' % rem)
					# print 'mask_parts: ', mask_parts
					for i in range(len(mask_parts), 4): #{
						mask_parts.append('0')
					#}
					# print 'mask_parts: ', mask_parts
				#}
				self.netmask = '.'.join(mask_parts)
			#}
			elif hasmask: #{
				self.bits = 0
				for octet in self.netmask.split('.'): 
					if not octet: break
					# print 'octet %s' % octet
					self.bits += _mask2bits[octet]
			else: #{
				self.netmask = '255.255.255.255'
				self.bits = 32
			#}}
		#}}
		# print cols
		self.netmask_bits = _a2b(self.netmask)
		# the next two lines fix the netmask if the original
		# argument as an IP address in the network with a netmask
		# or length (e.g. 192.168.1.1/255.255.255.0);
		self.network_bits = _a2b(self.network) & self.netmask_bits;
		self.network = _b2a(self.network_bits);
		if not 'broadcast' in cols: #{
			bmask = self.netmask_bits ^ _allones
			self.broadcast = _b2a(self.network_bits | bmask)
		#}
		self.broadcast_bits	= _a2b(self.broadcast)
		if self.bits == 32: #{{
			self.low_host = self.high_host = self.ipaddr
		#}
		else: #{
			self.low_host		= _b2a(self.network_bits | _b_one)
			self.high_host		= _b2a(self.broadcast_bits ^ _b_one)
		#}}
		if 'port' in cols and not 'protocol' in cols: #{
			self.protocol = 'tcp'
		#}
		self.cidr			= '%s/%s' % (self.network, self.bits)
		self.ipaddr			= IPaddr(self.ipaddr)
		if do_dnsname: #{
			self.dnsname	= dnsname(self.ipaddr)
		#}
		self.network		= IPaddr(self.network)
		self.low_host		= IPaddr(self.low_host)
		self.high_host		= self.low_host
		if self.bits != 32: #{
			self.high_host = IPaddr(self.high_host)
		#}
		for key in ('interface', 'macaddr'): #{
			if not key in cols: #{
				cols[key] = None
			#}
		#}
		# print repr(self.high_host)
	#}
	def ip2inaddr(self): #{
		'''Shortcut to return in-addr address'''
		return self.ipaddr.ip2inaddr()
	#} ip2inaddr

	def net2inaddr(self): #{
		'''Return network in-addr suitable for DNS zones'''
		return self.network.ip2inaddr().split('.', 1)[1]
	#} net2inaddr

	# Return the string version of the IP address.
	def __str__(self): #{
		'''string version of object (IP address)'''
		return(str(self.ipaddr))
		# return IPaddr.__str__(self.ipaddr)
	#}
	def includes(self, ipaddr): #{
		'''IP address is in range'''
		tmp = Netparams('%s/%s' % (ipaddr, self.netmask))
		return( str(tmp.network) == str(self.network) )
	#}
	def hostpart(self, ipaddr): #{
		'''Return host part of ipaddr'''
		if ipaddr is None: return None
		test_bits = _a2b('%s' % ipaddr)
		bmast = self.netmask_bits ^ _allones
		return(_b2a(bmask & test_bits))
	#}
	def ipchains_spec(self): #{
		'''Output suitable for use with ipchains'''
		output = self.cidr
		cols = self.__dict__
		if 'port' in cols:		output += ' %s' % self.port
		if 'protocol' in cols:	output += ' -p %s' % self.protocol
		return output
	#} ipchains_spec

	def iptables_spec(self, ipopt='--source', portopt='--dports'): #{
		'''Output suitable for use with iptables'''
		output = '%s %s' % (ipopt, self.cidr)
		cols = self.__dict__
		if 'port' in cols: #{
			ports = self.port.split(':')
			if len(ports) > 1: #{
				for port in range(int(ports[0])+1, int(ports[1])): #{
					ports.insert(1, str(port))
				#}
			#}
			output += ' %s %s' % (portopt, ','.join(ports))
		#}
		if 'protocol' in cols: output += ' --protocol %s' % self.protocol
		return output
	#} iptables_spec

	def dump(self): #{
		'''Dump instance hash'''
		keys = self.__dict__.keys()
		keys.sort()
		for key in keys: #{
			print '%-20s >%s<' % (key, self.__dict__[key])
		#}
	#} dump

	def ipsinblock(self): #{
		ipaddrs = []
		ipaddr = self.low_host
		hiaddr = self.high_host
		while ipaddr <= hiaddr: #{
			ipaddrs.append(ipaddr)
			ipaddr = ipaddr.incrip()
		#}
		return ipaddrs
	#} ipsinblock

#} class Netparams

privateNetworks = []

def isPrivate(ipaddr): #{
	'''Test to see if ipaddr is in private ranges'''
	global privateNetworks
	if not privateNetworks: #{
		from Csys.DNS import setDnsnameSilent
		saveit = setDnsnameSilent('isprivate')
		for network in ('192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12'): #{
			privateNetworks.append(Netparams(network))
		#}
		setDnsnameSilent(saveit)
	#}
	for network in privateNetworks: #{
		if network.includes(ipaddr): return True
	#}
	return False
#} isPrivate

NICs = {}

class NIC(Csys.CSClass): #{
	_attributes = {
		'iface'		: None,
		'ipaddr'	: None,
		'ip_sort'	: None,
		'netmask'	: None,
		'network'	: None,
		'hwaddr'	: None,
		'dnsname'	: None,
		'fname'		: None, # linux startup file
		'aliases'	: []
	}
	from glob import glob
	nicFiles = glob('/etc/sysconfig/network*/ifcfg-eth*')

	def __init__(self, **kwargs): #{
		Csys.CSClass.__init__(self, True, **kwargs)
		ipaddr = self.ipaddr
		self.network = Netparams('%s/%s' % (ipaddr, self.netmask))
		self.dnsname = dnsname(ipaddr)
		self.ip_sort = ip_sort(ipaddr)
		self.hwaddr = self.hwaddr.lower()
		self._getAliases()
		global NICs
		NICs[self.iface] = self
	#} __init__

	def _getAliases(self): #{
		'''Get aliases from configuration file'''
		ifcfgBasename = 'ifcfg-' + self.iface
		for file in self.nicFiles: #{{
			if os.path.basename(file) == ifcfgBasename: #{
				self.fname = file
				break
			#}
		#}
		else: #{
			# it only hits this else if it hasn't found a break
			# above.
			if self.nicFiles: #{
				prefx = ' '.join(self.nicFiles)
				grep = Csys.popen('grep -l %s %s' % (self.ipaddr, prefx))
				for file in grep: #{
					self.fname = file[:-1]
					break
				#}
				grep.close()
			#}
		#}}
		if self.fname: #{
			fh = open(self.fname)
			aliaslines = Csys.rmComments(fh,
				wantarray=True,
				pattern=r'^(IPADDR|NETMASK)_'
			)
			subpat = re.compile(r".*='(.*)'")
			for i in range(0, len(aliaslines), 2): #{
				ip, mask = (
					subpat.sub(r'\1', aliaslines[i]),
					subpat.sub(r'\1', aliaslines[i+1]),
				)
				alias = Netparams('%s/%s' % (ip, mask))
				alias.dnsname = dnsname(alias.ipaddr)
				self.aliases.append(alias)
			#}
		#}
	#} _getAliases

	def addAlias(self, ipaddr, netmask): #{
		'''Add alias to interface'''
		self.aliases.append(Netparams('%s/%s' % (network, netmask)))
	#} addAlias

	def __str__(self): return self.ipaddr

#} class NIC

def LinuxNICs(): #{
	'''Get NIC info from ifconfig command'''
	global NICs

	if NICs: return NICs

	def setNIC(iface): #{
		if 'hwaddr' in iface and 'ipaddr' in iface: #{
			ipPattern = re.compile(r'inet (\S+) .*secondary')
			nic = NIC(**iface)
			nicipaddr = str(nic.ipaddr)
			aliases = []
			cmd = 'ip addr show dev ' + nic.iface
			ipshow = Csys.popen(cmd)
			for line in ipshow: #{
				R = ipPattern.search(line)
				if R: #{
					ipaddr = Netparams(R.group(1))
					if ipaddr.ipaddr != nicipaddr: #{
						alias = Netparams(R.group(1))
						alias.dnsname = dnsname(alias.ipaddr)
						aliases.append(alias)
					#}
				#}
			#}
			if aliases: nic.aliases = aliases
		#}
	#} setNIC

	patterns = (
		('hwaddr',	re.compile(r'HWaddr\s+(\S+)')),
		('ipaddr',	re.compile(r'inet addr:(\S+)')),
		# ('bcast',	re.compile(r'Bcast:(\S+)')),
		('netmask',	re.compile(r'Mask:(\S+)')),
	)
	fh = Csys.popen('/sbin/ifconfig')
	newiface = re.compile(r'^(\S+)')
	iface = {}
	for line in fh: #{
		R = newiface.match(line)
		if R: #{
			if iface: setNIC(iface)
			iface = {'iface' : R.group(1)}
		#}
		for key, pattern in patterns: #{
			R = pattern.search(line)
			if R: iface[key] = R.group(1)
		#}
	#}
	fh.close()
	if iface: setNIC(iface)
	return NICs
#} LinuxNICs

def hexmask2octets(netmask): #{
	'''Convert 0xffffffff to netmask'''
	octets = []
	mask = netmask[2:]
	while mask: #{
		s, mask = eval('0x%s' % mask[:2]), mask[2:]
		octets.append('%d' % s)
	#}
	return '.'.join(octets)
#} hexmask2octets

def FreebsdNICs(): #{
	'''Get NIC info from ifconfig command'''
	global NICs

	if NICs: return NICs

	def setNIC(iface, aliases): #{
		if 'hwaddr' in iface and 'ipaddr' in iface: #{
			nic = NIC(**iface)
			ipaddrs = aliases['ipaddr']
			netmaskc = aliases['netmask']
			for i in range(0, len(ipaddrs)): #{
				nic.addAlias(ipaddrs[i], netmasks[i])
			#}
		#}
		return None
	#} setNIC

	patterns = (
		('hwaddr',	re.compile(r'\bether\s+(\S+)')),
		('ipaddr',	re.compile(r'\binet\b\s+(\S+)')),
		# ('bcast',	re.compile(r'broadcast\s+(\S+)')),
		('netmask',	re.compile(r'netmask\s+(\S+)')),
	)
	fh = Csys.popen('/sbin/ifconfig')
	newiface = re.compile(r'^(\S+)')
	iface = {}
	aliases = {}
	for line in fh: #{
		R = newiface.match(line)
		if R: #{
			if iface: setNIC(iface, aliases)
			iface = {'iface' : R.group(1)}
			aliases.update({
				'ipaddr'	: [],
				'netmask'	: [],
			})
		#}
		for key, pattern in patterns: #{
			R = pattern.search(line)
			if R: #{
				val = R.group(1)
				if key == 'netmask': val = hexmask2octets(val)
				if not key in iface: iface[key] = val
				elif key in aliases: aliases[key].append(val)
			#}
		#}
	#}
	fh.close()
	if iface: setNIC(iface, aliases)
	return NICs
#} FreebsdNICs

def SolarisNICs(): #{
	'''Get NIC info from ifconfig command'''
	global NICs

	if NICs: return NICs

	def setNIC(iface, aliases): #{
		if iface.has_key('hwaddr') and iface.has_key('ipaddr'): #{
			nic = NIC(**iface)
			ipaddrs = aliases['ipaddr']
			netmaskc = aliases['netmask']
			for i in range(0, len(ipaddrs)): #{
				nic.addAlias(ipaddrs[i], netmasks[i])
			#}
		#}
		return None
	#} setNIC

	patterns = (
		('hwaddr',	re.compile(r'\bether\s+(\S+)')),
		('ipaddr',	re.compile(r'\binet\b\s+(\S+)')),
		# ('bcast',	re.compile(r'broadcast\s+(\S+)')),
		('netmask',	re.compile(r'netmask\s+(\S+)')),
	)
	fh = Csys.popen('/sbin/ifconfig -a')
	newiface = re.compile(r'^(\S+)')
	iface = {}
	aliases = {}
	for line in fh: #{
		R = newiface.match(line)
		if R: #{
			if iface: setNIC(iface, aliases)
			iface = {'iface' : R.group(1)}
			aliases.update({
				'ipaddr'	: [],
				'netmask'	: [],
			})
		#}
		for key, pattern in patterns: #{
			R = pattern.search(line)
			if R: #{
				val = R.group(1)
				if key == 'netmask': val = hexmask2octets('0x' + val)
				if not iface.has_key(key): iface[key] = val
				# elif aliases.has_key(key): aliases[key].append(val)
			#}
		#}
	#}
	fh.close()
	if iface: setNIC(iface, aliases)
	return NICs
#} SolarisNICs

nicFunctions = {
	'darwin'	: FreebsdNICs,
	'freebsd'	: FreebsdNICs,
	'linux'		: LinuxNICs,
	'sunos'		: SolarisNICs,
}

def getNICs(): #{
	return nicFunctions[Csys.Config.ostype]()
#} getNICs

_gatewayPattern = re.compile(r'^(default|0\.0\.0\.0)\s+(\S+)')
def gateway(): #{
	'''Get gateway address from netstat -rn command'''
	for p in ('/bin', '/usr/bin', '/sbin', '/usr/sbin'): #{
		f = os.path.join(p, 'netstat')
		if os.path.exists(f): #{
			netstat = f
			break
		#}
	#}
	fh = Csys.popen(netstat + ' -rn')
	rc = ''
	for line in fh: #{
		R = _gatewayPattern.search(line)
		if R: #{
			rc = R.group(2)
			break
		#}
	#}
	fh.close()
	return rc
#} gateway

def publicip(): #{
	'''Return first public IP from NICs table'''
	NICs = getNICs()
	gw = gateway()
	for iface, nic in NICs.items(): #{
		# print 'iface >%s< nic >%s< ip >%s<' % (iface, nic, nic.ipaddr)
		net = nic.network
		if (gw and net.includes(gw) or not isPrivate(nic.ipaddr)): #{
			# print 'publicip = >%s<' % nic.ipaddr
			return net
		#}
	#}
	return None
#} publicip

def privateip(): #{
	'''Return first public IP from NICs table'''
	NICs = getNICs()
	gw = gateway()
	for iface, nic in NICs.items(): #{
		net = nic.network
		if isPrivate(nic.ipaddr) and not (gw and net.includes(gw)): #{
			return nic.network
		#}
	#}
	return publicip()
	# return Netparams('127.0.0.1/8')
#} privateip

_resolv_conf_nameserversPattern = re.compile(r'nameserver\s+(\S+)')

def nameservers(): #{
	'''Get name servers from /etc/resolv.conf'''
	nameservers = []
	fh = open('/etc/resolv.conf')
	for line in fh: #{
		R = _resolv_conf_nameserversPattern.match(line)
		if R: nameservers.append(R.group(1))
	#}
	return nameservers
#} nameservers

# The following routines are adapted from the perl Net::CIDR CPAN
# package.
#
# Copyright 2001-2003 Sam Varshavchik.
#
# with contributions from David Cantrell.
#
# This program is free software; you can redistribute it
# and/or modify it under the same terms as Perl itself.
#
# I (Bill Campbell <bill@celestial.com> have done the conversion
# from perl to python, and am solely responsible for my errors.
#
# The cidr2range routine is rewritten to use the Netparams class
# above as this eliminates all the bit manipulation from the
# original, shifting it to my kludges.
#

def cidr2range(cidr): #{
	'''Convert cidr to range of IP addresses'''
	isList = (type(cidr) == type([]))

	if isList: cidrs = cidr
	else: cidrs = [cidr]
	results = []
	for cidr in cidrs: #{
		N = Netparams(cidr)
		results.append('%s-%s' % (N.network, N.broadcast))
	#}
	if isList: return results
	return results[0]
#} cidr2range

_hexchars = '0123456789abcdef'

def _h62d(h): #{
	'''Convert 4 hex characters to dotted quad notation'''
	d = 0
	# make the conversion without bit fiddling
	for c in h: #{
		d = d * 16 + _hexchars.index(c)
	#}
	return ('%d.%d' % (int(d / 256), d % 256))
#} _h62d

def _hex2octets(R): #{
	'''Regular expression substitutions'''
	return _h62d(R.group(1))
#}

ipv6Pattern1 = re.compile(r'^[a-fA-F0-9:\.]+$')
ipv6Pattern2 = re.compile(r'^(.*:)([0-9]+\.[0-9\.]+)$')
ipv6Pattern3 = re.compile(r'([a-fA-F0-9]+)')
ipv6Pattern4 = re.compile(r'(.*)::(.*)')
ipv6Pattern5 = re.compile(r'[^0-9]+')
ipv6Pattern6 = re.compile(r'.')

def _ipv6to4(ipv6): #{
	'''Convert ipv6 to ipv4 string'''
	if ipv6.find(':') == -1: return((None, ipv6))

	if not ipv6Pattern1.match(ipv6): #{
		raise 'Syntax error: ' + ipv6
	#}

	ip4_suffix = ipv6_suffix = ''
	R = ipv6Pattern2.match(ipv6)
	if R: #{
		(ipv6, ip4_suffix) = (R.group(1), R.group(2))
	#}

	ipv6 = ipv6Pattern3.sub(_hex2octets, ipv6)

	R = ipv6Pattern4.search(ipv6)
	if R: #{{
		(ipv6, ipv6_suffix) = (R.group(1), R.group(2))
		ipv6_suffix += '.' + ip4_suffix
	#}
	else: #{
		ipv6 += '.' + ip4_suffix
	#}}
	p = Csys.grep(ipv6Pattern6, ipv6Pattern5.split(ipv6))
	s = Csys.grep(ipv6Pattern6, ipv6Pattern5.split(ipv6_suffix))
	while((len(p) + len(s)) < 16): p.append('0')
	p.extend(s)
	return (1, '.'.join(p))
#} _ipv6to4

ipv4tuple = tuple('0.0.0.0.0.0.0.0.0.0.255.255'.split('.'))
ipv4tupleLen = len(ipv4tuple)

def _ipv4to6(ipv4): #{
	'''ipv4 to ipv6'''
	octets = ipv6Pattern5.split(ipv4)
	assert len(octets) == 16, 'Invalid ipv4 >%s<' % ipv4
	
	top12 = tuple(octets[:ipv4tupleLen])
	if top12 == ipv4tuple: #{
		return('::ffff:' + '.'.join(octets[ipv4tupleLen:]))
	#}
	words = []
	for i in range(8): #{
		j = 2 * i
		words.append(
			'%x' % ((int(octets[j]) * 256) + int(octets[j+1]))
		)
	#}
	ind = indlen = -1
	i = 0
	while(i < 8): #{
		if words[i] != '0': #{
			j = i
			# emulate perlish behaviour
			for j in range(i, 8): #{{
				if words[j] == '0': break
			#}
			else: #{
				j = 8
			#}}
			if (j - i > indlen): #{
				indlen = j - i
				ind = i
				i = j - 1
			#}
		#}
		i += 1
	#}
	if indlen == 8: return('::')
	if ind < 0: return(':'.join(words))
	n = ind+indlen
	s = words[n:]
	words = words[:n]
	return(':'.join(words[:ind]) + '::' + ':'.join(s))
#} _ipv4to6

def addr2cidr(addr): #{
	'''Address to list of CIDR blocks'''
	isIPv6, addr = _ipv6to4(addr)
	assert not isIPv6, 'IPv6 unsupported at this time' + addr

	blocks = []
	for bits in range(8, 33): #{
		blocks.append(Netparams(addr, bits = bits).cidr)
	#}
	blocks.reverse()
	return blocks
#} addr2cidr

def addrandmask2cidr(addr, netmask): #{
	'''Address and netmask to CIDR'''
	return Netparams(addr, netmask = netmask).cidr
#} addrandmask2cidr

def _range2cidr8(a, b): #{
	a = int(a)
	b = int(b)
	assert (0 <= a <= 255), ('%d not in range 0 and 255' % a)
	assert (0 <= b <= 255), ('%d not in range 0 and 255' % b)
	assert (a <= b), ('%d not <= %d' % (a, b))
	b += 1
	c = []
	while(a < b): #{
		i = 0
		n = 1
		while((n & a) == 0): #{
			i += 1
			n = n << 1
			if i >= 8: break
		#}
		while(i > 0 and (n + a) > b): #{
			i -= 1
			n = n >> 1
		#}
		c.append(a)
		c.append(8 - i)
		a += n
	#}
	return c
#} _range2cidr8

def _range2cidr(a, b): #{
	# make local copies
	a = a[:]
	b = b[:]
	a0 = int(a.pop(0))
	b0 = int(b.pop(0))
	if not a: return _range2cidr8(a0, b0) # least significant octet pair.
	assert (0 <= a0 <= 255), '%d not in range 0 and 255' % a0
	assert (0 <= b0 <= 255), '%d not in range 0 and 255' % b0
	assert (a0 <= b0), '%d not <= %d' % (a0, b0)

	c = []
	if a0 == b0: #{
		cc = _range2cidr(a, b)
		while(cc): #{
			c0 = cc.pop(0)
			c.append('%s.%s' % (a0, c0))
			c0 = int(cc.pop(0))
			c.append(c0 + 8)
		#}
		return c
	#}
	start0 = end255 = True
	for x in a: #{
		if x != 0: start0 = False
	#}
	for x in b: #{
		if x != 255: end255 = False
	#}
	if not start0: #{
		bcopy = [255] * len(b) # array containing all 255s
		cc = _range2cidr(a, bcopy)
		while(cc): #{
			c0 = cc.pop(0)
			c.append('%s.%s' % (a0, c0))
			c0 = int(cc.pop(0))
			c.append(c0 + 8)
		#}
		a0 += 1
	#}
	if not end255: #{
		acopy = [0] * len(a) # array of zeros
		cc = _range2cidr(acopy, b)
		while(cc): #{
			c0 = cc.pop(0)
			c.append('%s.%s' % (b0, c0))
			c0 = int(cc.pop(0))
			c.append(c0 + 8)
		#}
		b0 -= 1
	#}
	if a0 <= b0: #{
		a = [0] * len(a) # set a array to all zeros
		pfix = '.'.join(a)
		cc = _range2cidr8(a0, b0)
		while(cc): #{
			c0 = cc.pop(0)
			c.append('%s.%s' % (c0, pfix))
			c.append(int(cc.pop(0)))
		#}
	#}
	return c
#} _range2cidr

# This pattern is public as it may be used in external routines
# such as those parsing rbldnsd files.
#
range2cidrPattern = re.compile(r'(.*)-(.*)')

def range2cidr(ranges, wantarray=True): #{
	('''Convert one or more ranges to CIDR blocks

	If wantarray is False or there's only a single entry in the
	resulting array, it will return a string, otherwise it will
	return a list of CIDR blocks.
	''')
	isList = type(ranges) == type([])
	if not isList: ranges = [ranges]
	c = []
	for range in ranges: #{
		# This allows us to pass a regular expression search
		# result as an argument which might be the case when
		# parsing files from rbldnsd.
		#
		if hasattr(range, 'group'): #{{
			R = range
		#}
		else: #{
			range = range.strip() # remove leading and trailing whitespace
			if _re_cidr.match(range): #{
				c.append(range)
				continue
			#}
			R = range2cidrPattern.match(range)
		#}}
		if R: #{{
			a = R.group(1).strip()
			b = R.group(2).strip()
		#}
		else: #{
			a = b = range
		#}}
		isipv6_a, a = _ipv6to4(a)
		isipv6_b, b = _ipv6to4(b)
		if (isipv6_a or isipv6_b): #{
			assert (isipv6_a == isipv6_b), (
				'cannot mix ipv4 and ipv6 >%s< >%s<' % (a, b)
			)
		#}
		# convert to arrays
		aList = a.split('.')
		bList = b.split('.')
		assert (len(aList) == len(bList)), (
			'ranges %s and %s octet mismatch' % (aList, bList)
		)
		cc = _range2cidr(aList, bList)
		while(cc): #{
			a0 = cc.pop(0)
			b0 = cc.pop(0)
			if isipv6_a: a0 = _ipv4to6(a0)
			c.append('%s/%s' % (a0, b0))
		#}
	#}
	if wantarray: return c
	return c[0]
#} range2cidr

def hex2ip(iphex): #{
	'''Convert hex string to octet'''
	return '.'.join([str(eval('0x' + iphex[i:i+2])) \
		for i in range(0,len(iphex), 2)
	])
#} hex2ip

if __name__ == '__main__': #{
	print 'OK'
	print hex2ip('c0a86f0f')
	print 'gateway: ', gateway()
	for iface, nic in  getNICs().items(): #{
		for alias in nic.aliases: #{
			print iface, alias, alias.dnsname
		#}
	#}
	print isPrivate('192.168.0.1')
	for n in privateNetworks: #{
		print '%4d %s' % ( n.bits, n.netmask )
	#}
	print Netparams('192.168.0.0/24').__dict__
	sys.exit(0)
	# from Csys.DNS import ipsinblock
	print isPrivate('192.136.111.1')
	pubip = publicip()
	print pubip.dnsname, pubip.ipaddr
	priip = privateip()
	print priip.dnsname, priip.ipaddr
	# the stuff below here is for testing.
	a = [255] * 3
	print a
	print 'range2cidr'
	print range2cidr([
		'192.136.111.7-192.136.111.33',
		# '192.136.111.45',
	])
	sys.exit(0)
	r = cidr2range('192.136.111.0/24')
	print r
	print range2cidr(r)
	# print '\n'.join([str(ip) for ip in ipsinblock('65.255.0.0/29')])
	l = 0
	for cidr in ('65.255.0.0/29', '65.255.1.0/29', '65.255.255.0/29' ): #{
		net = Netparams(cidr)
		print 'cidr: ', cidr, net.low_host, net.high_host, net.network, net.broadcast
		ip = net.low_host.incrip(255)
		print 'myincrip: ', type(ip)
		print 'network: ', net.network
		print 'type(net): ', type(net)
		print '\n'.join([repr(ip.ipaddr) for ip in net.ipsinblock()])
	#}
	print cidr2range(['192.168.0.0/16', '192.136.111.0/24'])
	net = Netparams('192.136.111.21')
	print net.__dict__.keys()
	iplong = net.ipaddr.ip2long()
	print 'ipaddr = >%s< iplong = %d' % (net.ipaddr, iplong)
	print net.ipaddr.long2ip(iplong + 255)
	print net.ipaddr.incrip(-255)
	sys.exit(0)
	print _h62d('ff03')
	(ok, ipv6) = _ipv6to4('::ffff:70.43.233.3')
	print ipv6
	print _ipv4to6(ipv6)
	print addr2cidr('192.136.111.7')

	bits = _a2b('255.255.255.0')
	print bits
	print _b2a(bits)

	ipnew = ipaddr.long2ip(iplong)
	print 'ipnew >%s<' % ipnew
	ipinc = ipnew.incrip(255)
	print 'ipinc >%s<' % ipinc
	cmp = ipinc.ipcmp(ipaddr)
	print 'cmp = %d' % cmp
	exit

	net = Netparams('192.136.111.130/25', port='nfs', protocol='udp')
	net.dump()
	print net.cidr
	print net
	print net.includes('192.136.111.127')
	print net.ipchains_spec()
	for i in range(3, -1, -1): #{
		print 'i = %d' % i
	#}
#}
