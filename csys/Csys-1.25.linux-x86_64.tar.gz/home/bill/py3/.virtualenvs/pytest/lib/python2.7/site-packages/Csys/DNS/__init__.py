# Celestial's DNS Utilities
__doc__='''Celestial Software's DNS Utilities

$Id: __init__.py,v 1.9 2009/11/25 01:55:55 csoftmgr Exp $'''

__version__='$Revision: 1.9 $'[11:-2]

import re, os, sys, time, datetime
import Csys

from socket import *

class rblTotals(object): #{
	'''Celestial Software's DNS Utilities'''
	def __init__(self, getrbls=False) : #{
		'''Initialize DNS utility object'''
		self.rbls		= []
		self.labels		= []
		self.hits		= []
		self.gotrbl		= {}
		self.rblmap		= {}
		self.nextlbl	= 'A'
		self.count		= 0
		self.rcstr		= ''
		self.ipcount	= 0
		if getrbls : self.getrblsfromhostsallow()
	#}
	rblPattern = re.compile(r'\{RBL\}\.(\S+).*DENY')
	def getrblsfromhostsallow(self): #{
		'''Get RBLs from /etc/hosts.allow'''
		fh = open('/etc/hosts.allow');
		for line in fh: #{
			i = line.find('#')
			if line > -1 : line = line[:i]
			line = line.strip()
			R = Utils.rblPattern.search(line)
			if R : self.addrbl(R.group(1))
		#}
	#}
	rblSubPattern = re.compile(r'\.*$')
	def addrbl(self, rblname): #{
		'''Add RBL to list'''
		rblname = rblSubPattern.sub('', rblname)
		if not rblname or rblname in self.gotrbl: return
		self.gotrbl[rblname]	= True
		n						= len(self.rbls)
		self.rblmap[rblname]	= n
		self.labels[n]			= self.nextlbl
		self.hits[n]			= 0;
		# this emulates perl's ++ on characters
		self.nextlbl			= chr(ord(self.nextlbl) + 1)
	#}
	def rbl_labels(self, printflag) : #{
		'''Generate list of lines summarizing table'''
		lines = [ 'Checked %d Addresses' % self.ipcount ]
		if self.ipcount == 1 : lines[0] = lines[0][:-2]
		for i in range(0, len(self.rbls)) : #{
			lines.append( ' %s %6d %s' % (
				self.labels[i], self.hits[i], self.rbls[i] )
			)
		#}
		if printflag : print '\n'.join(lines)
		return(lines)
	#}
	def rblcheck(self, ip, hits=1, first_only=False, pflag=False, rblhash=None) : #{
		self.ipcount += 1
		if len(self.rbls) == 0 : self.getrblsfromhostsallow()
		i = count = 0
		rc = ''
		for rbl in self.rbls : #{
			found = 'NOT '
			if not (count and first_only) and inrbl(ip, rbl, rblhash) : #{
				count += 1
				found = ''
				self.hits[i] += hits
				rc += self.labels[i]
			#}
			else : rc += '.'
			if pflag: #{
				sys.stderr.write('%s is %sRBL filtered by %s\n' % ( ip, found, rbl))
			#}
			i += 1
		#}
		self.count = count
		self.rcstr = rc
		return(count)
	#}
	def print_string(self) : return(self.rcstr)
	def print_count(self) : return(self.count)
#} rblTotals

def ip_sort(ip): #{
	'''ip_sort(ip) -> sortable version of IP address'''
	octets = ['%03d' % int(x) for x in str(ip).split('.', 4)[:4] ]
	return('.'.join(octets))
#} ip_sort

def long2ip(iplong): #{
	'''long2ip(iplong) -> ipstring where ip is a long'''
	octets = []
	for n in range(0, 5) : #{
		octets[n] = '%d' % (iplong % 256)
		iplong = iplong / 256
	#}
	octets.reverse()
	return('.'.join(octets))
#} long2ip

def ip2long(ip): #{
	'''ip2long(ip) -> long'''
	iplong = 0L
	for octet in ip.split('.', 4)[:4] : #{
		iplong = iplong * 256L + long(octet)
	#}
	return(iplong)
#} ip2long

etcHosts2IP = {}

etcIPs2Host = {}

ipaddrPattern = re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s*(.*)')

class EtcHosts(Csys.CSClass): #{
	_attributes = dict(
		ipaddr		= '',
		hostname	= '',
		hostnames	= []
	)
	def __init__(self, regex): #{
		self.ipaddr = ipaddr = regex.group(1)
		self.hostnames = hostnames = [
			s.strip() for s in regex.group(2).lower().split() if s.strip()
		]
		if hostnames: self.hostname = hostnames[0]
		if not ipaddr in etcIPs2Host: etcIPs2Host[ipaddr] = self
		for hostname in hostnames: #{
			if not hostname in etcHosts2IP: etcHosts2IP[hostname] = self
		#}
	#} __init__
#} class EtcHosts

def getEtcHosts(fname='/etc/hosts'): #{
	for line in Csys.grep('.', Csys.rmComments(open(fname), wantarray=True)): #{
		R = ipaddrPattern.match(line)
		if R and not R.group(1).startswith('127.'): #{
			obj = EtcHosts(R)
			# print obj.dumpAttrs()
		#}
	#}
#} getEtcHosts

getEtcHosts()

def dnsip(hostname, wantarray=False): #{
	'''dnsip(hostname, wantarray=False) -> ip'''
	hostname = hostname.lower().strip()
	host2ip = etcHosts2IP.get(hostname)
	if host2ip: #{
		# print 'host2ip: ', host2ip
		ip = host2ip.ipaddr
		if wantarray: ip = [ip]
		return ip
	#}
	try : #{{
		if not wantarray: return(gethostbyname(hostname))
		hostname, aliaslist, ipaddrlist = gethostbyname_ex(hostname)
		return ipaddrlist
	#}
	except : #{
		if wantarray: return []
		return None
	#}}
#} dnsip

# set to something to suppress dnsname lookups
_dnsnameSilent = ''

def getDnsnameSilent(): #{
	'''Get _dnsnameSilent value'''
	return _dnsnameSilent
#} getDnsnameSilent

def setDnsnameSilent(arg): #{
	'''
		External Interface for dnsnameSilent returning previous value
		This will allow one to save the old value for restoration
		with a single call.
	'''
	global _dnsnameSilent
	rc = _dnsnameSilent
	_dnsnameSilent = arg
	return rc
#} setDnsnameSilent

def dnsname(ip, hostname=None): #{
	'''dnsname(ip) => hostname'''
	if hostname is None: hostname = _dnsnameSilent
	if not hostname: #{
		hostobj = etcIPs2Host.get(ip)
		if hostobj: #{{
			hostname = hostobj.hostname
		#}
		else: #{
			# print 'dnsname(%s)' % ip
			try: hostname, aliaslist, ipaddrlist = gethostbyaddr(str(ip))
			except : hostname = None
			if hostname is None: #{
				cmd = '%s %s' % (os.path.join(Csys.prefix, 'bin/dnsname'), ip)
				fh = Csys.popen(cmd)
				hostname = fh.readline().strip()
				fh.close()
			#}
		#}}
		# print 'hostname(%s)' % hostname
	#}
	return hostname
#} dnsname

class Rrecord(Csys.CSClass): #{
	'''Super class for other DNS classes'''
	_attributes = {
		'fqdn'		: '',
		'ip'		: '',
		'ttl'		: '',
		'timestamp'	: '',
		'suffix'	: '',
	}
	def __init__(self, djbdns=None, **kwargs): #{
		'''Default initialization

		djbdns is the line from a tinydns data file
		'''

		Csys.CSClass.__init__(self, **kwargs)
		if djbdns: #{
			d = dict(zip(self.djbdnsFields, djbdns[1:].split(':')))
			self.__dict__.update(d)
			# print self.__dict__
			# print 'fqdn = >%s<' % self.fqdn
		#}
	#} __init__

	def djbdnsOutput(self, local=True): #{
		entry = Csys.CSClassBase(self.__dict__)
		if not local: #{
			if entry.suffix == 'ex': entry.suffix = ''
			if entry.suffix: return('')
		#}
		output = self.djbdnsPrefix + ':'.join([
			str(x) for x in Csys.getSlice(self.djbdnsFields, entry.__dict__)
		])
		# print 'suffix >%s<\n\t%s' % (self.suffix, output)
		return output
	#} djbdnsOutput
#} Rrecord

_defaultTimes = 3600 * 24 # one day

class SOArecord(Rrecord): #{
	_attributes = {
		'ns'			: '',
		'contact'		: '',
		'serial'		: '',
		'refresh'		: _defaultTimes,
		'retry'			: _defaultTimes,
		'expire'		: _defaultTimes,
		'minimum'		: _defaultTimes,
		'classname'		: 'SOArecord',
	}
	_attributes.update(Rrecord._attributes)

	djbdnsPrefix = 'Z'

	djbdnsFields = (
		'fqdn:ns:contact:serial:refresh:retry:expire:minimum:ttl:timestamp:suffix'.split(':')
	)
	def __init__(self, djbdns=None, **kwargs): #{
		'''SOA Record initialzation'''

		Rrecord.__init__(self, djbdns, **kwargs)
		contact, n = self.contact, self.contact.find('@')
		if n != -1: self.contact = contact[:n-1] + '.' + contact[n+1:]
	#} __init__
#} SOArecord

class NSrecord(Rrecord): #{
	_attributes = {
		'nsfqdn'	: '',
		'classname'	: 'NSrecord',
	}
	_attributes.update(Rrecord._attributes)

	djbdnsPrefix = '.'
	djbdnsFields = 'fqdn:ip:nsfqdn:ttl:timestamp:suffix'.split(':')

	def __init__(self, djbdns=None, **kwargs): #{
		'''NS Record'''

		Rrecord.__init__(self, djbdns, **kwargs)
		if self.nsfqdn.find('.') == -1: #{
			self.nsfqdn = '%s.ns.%s' % (self.nsfqdn, self.fqdn)
		#}
	#} __init__
#} NSrecord

class NSrecordDelegate(NSrecord): #{
	_attributes = {
		'nsfqdn'	: '',
		'classname'	: 'NSrecordDelegate',
	}
	_attributes.update(Rrecord._attributes)

	djbdnsPrefix = '&'

#} NSrecordDelegate

class HostRecord(Rrecord): #{
	'''DJBDNS record mapping forward and reverse DNS'''
	_attributes = dict(classname = 'HostRecord')
	_attributes.update(Rrecord._attributes)

	djbdnsPrefix = '='
	djbdnsFields = 'fqdn:ip:ttl:timestamp:suffix'.split(':')
#} class HostRecord

class HostRecordAlias(Rrecord): #{
	'''DJBDNS record mapping forward and reverse DNS'''
	_attributes = dict(classname = 'HostRecordAlias')
	_attributes.update(Rrecord._attributes)

	djbdnsPrefix = '+'
	djbdnsFields = 'fqdn:ip:ttl:timestamp:suffix'.split(':')
#} class HostRecord

class MXrecord(Rrecord): #{
	djbdnsPrefix = '@'
	djbdnsFields = 'fqdn:ip:mxhost:dist:ttl:timestamp:suffix'.split(':')
	_attributes = {
		'dist'		: 1,
		'mxhost'	: '',
		'classname'	: 'MXrecord',
	}
	_attributes.update(Rrecord._attributes)

	def __init__(self, djbdns=None, **kwargs): #{
		'''MX Record Initialization'''
		Rrecord.__init__(self, djbdns, **kwargs)
		if self.mxhost.find('.') == -1: #{
			self.mxhost = '%s.mx.%s' % (self.mxhost, self.fqdn)
		#}
	#} __init__
#} MXrecord

class TXTrecord(Rrecord): #{
	djbdnsPrefix = "'"
	djbdnsFields = 'fqdn:text:ttl:timestamp:suffix'.split(':')
	_attributes = {
		'text'		: '',
		'classname'	: 'TXTrecord',
	}
	_attributes.update(Rrecord._attributes)
#} TXTrecord

class PTRrecord(Rrecord): #{
	djbdnsPrefix = "^"
	djbdnsFields = 'fqdn:p:ttl:timestamp:suffix'.split(':')
	_attributes = {
		'p'			: '',
		'classname'	: 'PTRrecord',
	}
	_attributes.update(Rrecord._attributes)
#} PTRrecord

class CNAMErecord(Rrecord): #{
	djbdnsPrefix = 'C'
	djbdnsFields = 'fqdn:realname:ttl:timestamp:suffix'.split(':')
	_attributes = {
		'realname'	: '',
		'classname'	: 'CNAMErecord',
	}
	_attributes.update(Rrecord._attributes)
#} CNAMErecord

class GENrecord(Rrecord): #{
	'''Generic Record'''
	djbdnsPrefix = ":"
	djbdnsFields = 'fqdn:n:rdata:ttl:timestamp:suffix'.split(':')
	_attributes = {
		'n'			: '',
		'rdata'		: '',
		'classname'	: 'GENrecord',
	}
	_attributes.update(Rrecord._attributes)
#} PTRrecord

djbdnsMap = {
	SOArecord.djbdnsPrefix			: SOArecord,
	CNAMErecord.djbdnsPrefix		: CNAMErecord,
	HostRecord.djbdnsPrefix			: HostRecord,
	HostRecordAlias.djbdnsPrefix	: HostRecordAlias,
	MXrecord.djbdnsPrefix			: MXrecord,
	NSrecord.djbdnsPrefix			: NSrecord,
	NSrecordDelegate.djbdnsPrefix	: NSrecordDelegate,
	TXTrecord.djbdnsPrefix			: TXTrecord,
	PTRrecord.djbdnsPrefix			: PTRrecord,
	GENrecord.djbdnsPrefix			: GENrecord,
}
djbdnsPrefixes = []

# map of all domains
domainMap = {}

def getDomain(fqdn): #{
	'''Find domain in domainMap that contains fqdn'''
	global domainMap

	parts = Csys.grep('.', fqdn.split('.'))
	while parts: #{
		domain = domainMap.get('.'.join(parts))
		if domain: return domain
		parts.pop(0)
	#}
	return None
#} getDomain

class Domain(Csys.CSClass): #{
	_attributes = {
		'fqdn'				: '',
		'SOArecord'			: None,
		'CNAMErecord'		: {},
		'HostRecord'		: {},
		'HostRecordAlias'	: {},
		'MXrecord'			: {},
		'NSrecord'			: {},
		'NSrecordDelegate'	: {},
		'TXTrecord'			: {},
		'PTRrecord'			: {},
		'GENrecord'			: {},
		'_seq'				: 0,
		'filename'			: '', # file to read/write
		'dirname'			: '', # parent two levels up from filename
	}
	_plainAttributes = []
	_dicttype = type({})
	for attr, val in _attributes.items(): #{
		if type(val) != _dicttype: _plainAttributes.append(attr)
	#}

	def __init__(self, djbdns=None, **kwargs): #{

		global djbdnsMap

		Csys.CSClass.__init__(self, **kwargs)
		if djbdns: #{
			prefix		= djbdns[0]
			self.fqdn	= djbdns[1:djbdns.find(':')].rstrip('.')
			if prefix == SOArecord.djbdnsPrefix: #{{
				self.SOArecord = SOArecord(djbdns, **kwargs)
			#}
			elif prefix == NSrecord.djbdnsPrefix: #{
				self._seq += 1
				self.NSrecord[self._seq] = NSrecord(djbdns, **kwargs)
			#}}
		#}
		global domainMap
		domainMap[self.fqdn] = self
	#} __init__

	def __setattr__(self, attr, val): #{
		'''Push entry in array if not 'fqdn' or SOArecord'''
		cols = self.__dict__
		if attr in self._plainAttributes: cols[attr] = val
		else: #{
			self._seq += 1
			cols[attr][self._seq] = val
		#}
	#} __setattr__

	_toleadingDot = re.compile(r".*\.(.*)'>$")

	def addAttribute(self, djbdns=None, **kwargs): #{
		'''Add Attribute to appropriate table'''
		if djbdns: #{
			prefix = djbdns[0]
			try: #{
				obj = djbdnsMap[prefix](djbdns, **kwargs)
				myclass = obj.classname
				self.__setattr__(myclass, obj)
			except KeyError:
				sys.stderr.write('invalid key >%s<\n' % djbdns)
				sys.stderr.write('%s\n' % self.dumpAttrs())
				sys.stderr.write('class >%s< myclass >%s<\n' % (obj, myclass))
				sys.stderr.write('class >%s<\n' % obj.__class__)
				raise
			#}
		#}
	#} addAttribute

	_outputOrder = (
		('NSrecord',		'Name Server Records'),
		('NSrecordDelegate','Delegated Name Server Records'),
		('HostRecord',		'Host Records'),
		('HostRecordAlias',	'Host Aliases'),
		('MXrecord',		'Mail eXchange Records'),
		('CNAMErecord',		'CNAME records (deprecated)'),
		('TXTrecord',		'Text records'),
		('PTRrecord',		'PTR reverse DNS records'),
		('GENrecord',		'Generic records'),
	)

	def djbdnsOutput(self, local=True): #{
		'''Generate djbdns output'''
		output = [self.SOArecord.djbdnsOutput(local)]
		cols = self.__dict__
		for attr, desc in self._outputOrder: #{
			d = cols[attr]
			keys = d.keys()
			if keys: #{
				output.append('\n# %s\n\n' % desc)
				keys.sort()
				for key in keys: #{
					output.append(d[key].djbdnsOutput(local))
				#}
			#}
		#}
		return output
	#} djbdnsOutput

	def djbdnsWriteFile(self, filename=None, local=True): #{
		'''Write djbdns zone records to file'''
		global djbdnsPrefixes

		if filename is None: filename = self.filename
		if filename: #{
			if hasattr(filename, 'write'): #{{
				fh = filename
				filename = fnamenew = None
			#}
			elif os.path.isfile(filename): #{{
				fnamenew = filename + '.new'
				fh = Csys.openOut(fnamenew, model=filename)
			#}
			else: #{
				fnamenew = filename
				fh = Csys.openOut(fnamenew)
			#}}
			if local and djbdnsPrefixes:
				fh.write('%s\n\n' % '\n'.join(djbdnsPrefixes))

			fh.write('%s\n' % '\n'.join(self.djbdnsOutput(local)))
			if not filename is None: fh.close()
			if fnamenew != filename: #{
				fnamebak = filename + '.bak'
				os.rename(filename, fnamebak)
				os.rename(fnamenew, filename)
			#}
		#}
	#} djbdnsWriteFile
#} Domain

def djbdnsReadFiles(args=[]): #{
	'''Read Domain(s) from djbdns files'''

	global djbdnsPrefixes

	if not args: #{
		from glob import glob
		'''Get file lists from /csoft/etc/djbdns/{primary,private}'''
		djbdnsdir = os.path.join(Csys.prefix, 'etc/djbdns')
		os.chdir(djbdnsdir)
		args = ( glob('primary/*/data') + glob('private/*/data') )
		args.sort()
	#}
	for arg in args: #{
		# sys.stderr.write('processing %s\n' % arg)
		fh = open(arg)
		lines = Csys.rmComments(fh, wantarray=True)
		for line in Csys.grep(r'^Z', lines): #{
			obj = Domain(line)
			obj.filename = arg
			obj.dirname = os.path.dirname(os.path.dirname(arg))
		#}
	#}
	for arg in args: #{
		fh = open(arg)
		lines = Csys.rmComments(fh, wantarray=True)
		curdomain = None
		for line in lines: #{
			if not line: continue
			prefix = line[0]
			fqdn = line[1:].split(':', 1)[0].rstrip('.')
			if prefix == 'Z': #{{
				curdomain = domainMap[fqdn]
			#}
			elif prefix == '%': #{
				if not line in djbdnsPrefixes: djbdnsPrefixes.append(line)
			#}
			else: #{
				domain = getDomain(fqdn)
				if not domain: domain = curdomain
				if not domain: #{
					sys.stderr.write('badfqdn %s\n\t%s\n' % (fqdn, line))
					continue
				#}
				# curdomain = domain
				domain.addAttribute(line)
			#}}
		#}
	#}
	return domainMap
#} djbdnsReadFiles

class dnsMX(object): #{
	'''MX Record'''
	def __init__(self, distance, host, wantip=False, wantarray=False) : #{
		self.distance		= int(distance)
		self.host			= host
		if wantip:	self.ip	= dnsip(host, wantarray=wantarray)
		else:		self.ip	= None
	#}

	def __cmp__(self, other): #{
		return cmp((self.distance, self.host), (other.distance, other.host))
	#} __cmp__
#} dnsMX

def dnsmx(addr, wantip=False, wantarray=False): #{
	'''Get MX address(es)'''
	# remove local part
	addr = addr[addr.find('@')+1:]
	fh = Csys.popen('%s %s' % (os.path.join(Csys.prefix, 'bin/dnsmx'), addr))
	mxrecs = []
	for line in fh: #{
		distance, host = line.split()
		mxrecs.append(dnsMX(distance, host, wantip, wantarray))
	#}
	if not mxrecs: return None
	mxrecs.sort()
	if not wantarray: #{
		if wantip: return mxrecs[0].ip
		return mxrecs[0].host
	#}
	return mxrecs
#} dnsmx

def inrbl(ip, rblname, rblhash=None): #{
	'''inrbl(ip, rblname, rblhash=None) -> boolian if ip is in rbl'''
	if not rblname: return None
	# make rblname absolute
	if rblname[-1:] != '.' : rblname = rblname + '.'
	if rblhash : return(rblhash.get(rblname))
	octets = ip.split('.')
	octets.reverse()
	octets.append(rblname)
	testhost = '.'.join(octets)
	try: return(gethostbyname(testhost))
	except : return None
#} inrbl

import Csys.Netparams

def ipsinblock(network, LowAddr=None): #{
	'''return sorted array with all IPs in block.'''
	if not isinstance(network, Csys.Netparams.Netparams): #{
		network = Csys.Netparams.Netparams(network)
	#}
	if not LowAddr : LowAddr = network.low_host
	HiAddr = ip_sort(network.high_host)
	ip = LowAddr
	ips_available = []
	while(ip_sort(ip) <= HiAddr) : #{
		ips_available.append(ip)
		ip = ip.incrip(1)
	#}
	return(ips_available)
#} ipsinblock

def availableips(network, LowAddr=None, NumberRequested=0): #{
	'''get available IP addresses from CIDR block'''
	if not isinstance(network, Csys.Netparams.Netparams): #{
		network = Csys.Netparams.Netparams(network)
	#}
	ips_available = []
	for ip in ipsinblock(network, LowAddr) : #{
		hostname = dnsname(ip)
		if hostname : continue
		if NumberRequested == 1 : return(ip)
		ips_available.append(ip)
		if (NumberRequested and len(ips_available) >= NumberRequested) : break
	#}
	return ips_available
#} availableips

def mapips(network, LowAddr=None): #{
	'''mapips(network, LowAddr=None) -> dictionary of IP names with sortable keys'''
	if not isinstance(network, Csys.Netparams.Netparams): #{
		network = Csys.Netparams.Netparams(network)
	#}
	ipnames = {}
	for ip in ipsinblock(network, LowAddr) : #{
		hostname = dnsname(ip)
		key = ip_sort(ip)
		if hostname : ip = '%s\t# %s' % (ip, hostname)
		ipnames[key] = ip
	#}
	return ipnames
#} mapips

def ip2inaddr(ip, domain='in-addr.arpa'): #{
	'''Convert IP address to in-addr notation'''
	octets = ip.split('.', 4)[0:4]
	octets.reverse()
	if domain : octets.append(domain)
	return('.'.join(octets))
#} ip2inaddr

if __name__ == '__main__' : #{
	print 'OK'
	# print etcHosts2IP
	# print etcIPs2Host
	print dnsname('192.168.253.33')
	print dnsip('ayn', True)
	print dnsip('jgmkens1vm1.mi.celestial.com')
	print dnsip('ayn.mi.celestial.com')
	sys.exit(0)
	mxrecs = dnsmx('bill@aaauniform.com', wantip=True, wantarray=True)
	for mx in mxrecs: #{
		print mx.__dict__
	#}
	mx = dnsmx('bill@aaauniform.com', wantip=True)
	print mx
	print dnsip(mx, wantarray=True)
	print ip_sort(dnsip('10.136.111.7'))
	print inrbl('192.136.111.7', 'rbl.celestial.net')
	print inrbl('219.115.87.82', 'rbl.celestial.net')
	print ip2inaddr('192.136.111.7')
#}
