#!/usr/local/bin/python

__doc__='''Internet mail utilities

This provides a similar interface to the perl Mail::Internet
package, with hopefully a simpler interface to input and the body
of the messages.

$Id: MailInternet.py,v 1.8 2009/11/25 02:17:20 csoftmgr Exp $'''

__version__='$Revision: 1.8 $'[11:-2]

import os, sys, re, email
# Python 2.6 (and possibly earlier).
try: #{{
	from hashlib import md5
#}
except ImportError: #{
	from md5 import new as md5
#}}
import time
import Csys
from email.Utils import parsedate_tz, mktime_tz, formatdate

from email.Parser import Parser
from Csys.Dates import getdate, today, DF_MAIL, rfcDate
from Csys.SysUtils import getStringFromFiles

_verbose = False

import email.Message

_reHeaderBody = re.compile(r'(.*?\n\n)(.*)', re.DOTALL)

_typeRE = type(_reHeaderBody)

# Received: header patterns
# This one works with postfix and smail-3.2 at least
_receivedPatterns = (
	re.compile(
		r'^from\s+(?P<helo>\S+)\s*\(' 		# HELO part
		r'(?P<dnsname>\S*)\s*\[(?P<ip>[^]]*)\]'		# dnsname and ip address
		r'\)'						# end HELO
		r'.*\sby\s(?P<by>\S+)'			# received by
		r'.*^\s*id[^;]*;\s*(?P<date>.*)$'	# DATE
		# r'\bid\s+\S+\s+(?P<date>.*)'
		, re.MULTILINE | re.DOTALL
	),
	re.compile(
		r'^from\s*(?P<helo>\S+)\s*\(' 		# HELO part
		r'(?P<dnsname>\S*)\s*\[(?P<ip>[^]]*)\]'		# dnsname and ip address
		r'\)'						# end HELO
		r'.*\sby\s(?P<by>\S+)'			# received by
		r'.*^\s*for[^;]*;\s*(?P<date>.*)$'	# DATE
		, re.MULTILINE | re.DOTALL
	),
	re.compile(
		r'^from\s*(?P<helo>[-\.\d]+)\s*\(' 		# HELO part
		r'\[(?P<ip>[^]]*)\]'		# dnsname and ip address
		r'\)'						# end HELO
		# r'.*\sby\s(?P<by>\S+)'			# received by
		r'.*^\s*for[^;]*;\s*(?P<date>.*)$'	# DATE
		, re.MULTILINE | re.DOTALL
	),
	re.compile(
		r'\[(?P<ip>[^\]]*)\]'				# IP
		r'.*\sby\s(?P<by>\S+)'			# received by
		r'.*^\s*for[^;]*;\s*(?P<date>.*)$'	# DATE
		, re.MULTILINE | re.DOTALL
	),
)
# bad date format for rewrite in msgdate
_dateRE = re.compile(
	r'^(\w+,\s+\d{1,2}\s+\w+\s+)(\d{1,3})(\s+\d{1,2}:\d{1,2}:\d{1,2}.*)$'
)

class Received(Csys.CSClass): #{
	__doc__ = Csys.detab('''
	Class to extract relevant info from Received: headers
	''')
	_attributes = {
		'helo'		: None,
		'dnsname'	: None,
		'ip'		: None,
		'date'		: None,
		'by'		: None,
		'received'	: None, # original received
	}
	def __init__(self, received): #{
		'''Disect received header'''
		Csys.CSClass.__init__(self)
		self.received = received
		if received.startswith('Received:'): received = received[8:]
		if _verbose: sys.stderr.write('Received: %s\n' % received)
		i = 0
		for pattern in _receivedPatterns: #{
			i += 1
			R = pattern.search(received)
			if R: #{
				if _verbose: #{
					sys.stderr.write('\t%d \n\t%s\n' % (
						i, '\n\t'.join(R.groups())
					))
				#}
				try: #{
					self.helo		= R.group('helo')
					self.dnsname	= R.group('dnsname')
					if not self.dnsname: self.dnsname = self.helo
					self.by			= R.group('by')
				#}
				except: pass
				self.ip			= R.group('ip')
				self.date		= R.group('date')
				break
			#}
		#}
	#}

	def utime(self): #{
		'''Return utime from date'''
		return long(mktime_tz(parsedate_tz(self.date)))
	#} utime

#} class Received

# SpamAssassin support
import spamd
SpamdConnection = spamd.SpamdConnection
SPAMD_PORT = spamd.SPAMD_PORT

class Message(Csys.CSClass): #{
	_attributes = {
		'msg'			: None, # python email.Message
		'msgstr'		: None,
		'headerstr'		: None,
		'bodystr'		: None,
		'sender'		: None,
		'_HdrDict'		: {},
		'sa_spam'		: False, # True if SA identifies it as spam
		'sa_score'		: 0,
		'sa_required'	: 0,
		'sa_symbols'	: '',
		'sa_version'	: '',
		'_md5'			: None,
	}
	'''Internet Mail Message Instance'''
	def __init__(self, *args): #{
		Csys.CSClass.__init__(self)
		msgstr			= getStringFromFiles(*args)
		R				= _reHeaderBody.match(msgstr)
		header, body	= R.groups()
		# print 'msgstr >%s<' % msgstr
		self.msg		= Parser().parsestr(msgstr)
		self.headerstr	= header
		self.bodystr	= body
		# Deliver will have this environment variable set, and others may.
		self.sender		= os.environ.get('SENDER')
		if self.sender is None: self.sender = self._getSender()
	#} __init__

	# Return list of body lines
	def body(self): return(self.bodystr.split('\n'))

	def print_header(self, fh = sys.stdout): fh.write(self.headerstr)

	def print_body(self, fh = sys.stdout): fh.write(self.bodystr)

	# This cannot be named ``print'' as it's a syntax error
	def print_msg(self, fh=sys.stdout): fh.write(self.msg.as_string())

	# Header routines for perl Mail::Internet compatibility
	def add(self, tag, line): #{
		'''Add header type tag'''
		# print 'add: tag ', tag
		# print 'add: line ', line
		line = str(line)
		self.msg.add_header(tag, line)
	#} add

	def replace(self, tag, line): #{
		'''Replace header'''
		line = str(line)
		try:
			self.msg.replace_header(tag, line)
		except KeyError:
			self.msg.add_header(tag, line)
	#} replace

	def get(self, tag, failobj=None, index=0): #{
		'''Get header with optional index'''
		name = tag.lower()
		hdr_ndx = 0
		for k, v in self.msg._headers: #{
			if k.lower() == name: #{
				if hdr_ndx == index: return v
				hdr_ndx += 1
			#}
		#}
		return failobj
	#} get

	def delete(self, tag, index=None): #{
		'''Delete header'''
		if index is None:
			self.msg.__delitem__(tag)
			return
		name = tag.lower()
		newheaders = []
		hdr_ndx = 0
		for k, v in self.msg._headers: #{
			if k.lower() == name: #{
				if hdr_ndx == index: continue
				hdr_ndx += 1
			#}
			newheaders.append(k, v)
		#}
		self.msg._headers = newheaders
	#} delete

	def count(self, tag): #{
		'''Return count of header items'''
		if not self.msg.has_key(tag): return 0
		headers = self.msg.get_all(tag)
		return(len(headers))
	#} count

	def tags(self): return (self.msg.keys())

	def __str__(self): return(self.msg.as_string(False))

	def md5(self, addheader=True): #{
		'''Return md5 digest of message body'''
		if self._md5 is None: #{
			self._md5 = chksum = md5(self.bodystr).hexdigest()
			if addheader: #{
				hdr = 'X-Csys-md5body'
				self.replace(hdr, chksum)
			#}
		#}
		return self._md5
	#} md5

	# Python email.Message method pass through
	def get_all(self, tag): #{
		'''Get all headers of type tag'''
		# print 'get_all(%s)' % tag
		return self.msg.get_all(tag, [])
	#} get_all

	def grep(self, hdrs, pattern, exists=False): #{
		'''Return headers that match pattern
		
		This is intended to parse the host.allow style lines in a
		mailbox patterns file.  Setting exists to the mailbox name
		will return that name.
		'''
		msg = self.msg
		if type(pattern) == _typeRE: pat = pattern
		else: #{
			try: pat = re.compile(pattern, re.IGNORECASE|re.DOTALL|re.MULTILINE)
			except: return None
		#}
		matches = []
		for tag in hdrs.split(','): #{
			tag = tag.strip().lower()
			for hdr in self.get_all(tag): #{
				if pat.search(hdr): #{
					if exists: return exists
					matches.append(hdr)
				#}
			#}
		#}
		return matches
	#} grep

	def msgdate(self): #{
		'''Return Date: header or date from first parsable Recieved'''

		saveDate = origDate = Date = self.get('Date')
		datetuple = parsedate_tz(Date)
		if not datetuple: #{
			origDate = None # bad date or need to parse
			received_hdrs = self.get_all('received');
			for received in received_hdrs: #{
				Date = Received(received).date
				if not Date: continue
				datetuple = parsedate_tz(Date)
				if datetuple: break
			#}
		#}
		try: #{{
			if datetuple: utime = mktime_tz(datetuple)
			else: utime = time.time()
		#}
		except: utime = time.time() #}

		if origDate is None: #{
			self.replace('X-Orig-date', saveDate)
			self.replace('Date', Date)
		#}
		return long(utime)
	#} msgdate

	def get_unixfrom(self): return self.msg.get_unixfrom()

	def _getSender(self): #{
		'''Get sender from Unix From'''
		sender = self.msg.get_unixfrom()
		if sender: sender = sender.split()[1]
		return sender
	#} _getSender

	def checkSpamAssassin(self, user, host='localhost', port=SPAMD_PORT,
		subjectprefix='***SPAM***'):
	#{
		'''Check message against spamassassin'''
		conn = SpamdConnection(host, int(port))
		conn.addheader('User', user)
		conn.check(spamd.SYMBOLS, str(self))
		self.sa_version = conn.server_version
		response = conn.response_headers['Spam']
		is_spam, score = response.split(';')
		is_spam = (is_spam.strip() != 'False')
		score, required = [float(x) for x in score.split('/')]
		self.rmSAHeaders() # get rid of all old spam markers
		self.sa_spam, self.sa_score, self.sa_required = (
			is_spam, score, required
		)
		self.sa_symbols = conn.response_message.replace(',', ', ')
		# now update the headers
		if is_spam: #{
			spamflag = 'Yes'
			if subjectprefix:
				self.replace('Subject', subjectprefix + self.get('subject', ''))
		#}
		else: spamflag = 'No'

		self.replace('X-Spam-Flag', spamflag.upper())
		if score > 0: self.replace('X-Spam-Level' , '*' * int(score))
		self.replace('X-Spam-Status',
			'%s, score=%.2f required=%.2f tests=%s\n\twith spamd' %
			(spamflag, score, required, self.sa_symbols)
		)
		return self.sa_spam
	#} checkSpamAssassin

	_saCommentPatterns = (
		re.compile(r'^\*+SPAM\*+\s+'),
		re.compile(r'^\[SPAM\]\s+'),
	)
	def rmSAHeaders(self): #{
		'''Remove Spamassassin headers and modify Subject'''
		subject = self.get('subject')
		for pattern in self._saCommentPatterns: #{
			try: newsubject = pattern.sub('', subject)
			except: continue
			if newsubject != subject: #{
				self.replace('subject', newsubject)
				break
			#}
		#}
		self.delete('X-Spam-Checker-Version')
		self.delete('X-Spam-Flag')
		self.delete('X-Spam-Level')
		self.delete('X-Spam-Status')
		self.delete('X-Spam-Report')
		self.delete('X-Spam-Score')
		self.delete('X-Spam')
		self.delete('X-Barracuda-Spam-Score')
		self.delete('X-Barracuda-Spam-Status')
		self.delete('X-Barracuda-Spam-Report')
	#} rmSAHeaders

	def firstReceived(self, whl='whl.celestial.net', mxips=[]): #{
		if whl or mxips: #{
			from Csys.DNS import inrbl
			from Csys.Netparams import isPrivate
			received_hdrs = self.get_all('received');
			for received in received_hdrs: #{
				received = Received(received)
				if received.ip: #{
					try: #{{
						ipaddr = received.ip
						if not (
							ipaddr.startswith('127.')
							or isPrivate(ipaddr)
							or (ipaddr in mxips)
							or (whl and inrbl(ipaddr, whl))
						): return received
					#}
					except: pass #}
				#}
			#}
		#}
		return None
	#} firstReceived

#} Message

class PostfixConfig(Csys.CSClass): #{
	'''Get Postfix Configuration from postconf'''
	def __init__(self, fh=None): #{
		'''Read postconf output'''
		if fh: #{{
			if not hasattr(fh, 'readlines'): fh = open(fh)
		#}
		else: #{
			fh = Csys.popen(os.path.join(Csys.prefix, 'sbin/postconf'))
		#}}
		cols = self.__dict__
		for line in fh: #{
			line = line.strip()
			parts = line.split('=', 1);
			var = parts.pop(0).strip()
			try: val = parts[0]
			except: val = None
			cols[var] = val.strip()
		#}
		fh.close()
		self.expandvars()
	#} __init__

	_varPattern = re.compile(r'\$([{}0-9a-z_]*)', re.IGNORECASE)
	def expandvars(self): #{
		'''Expand variable names in values'''
		subs = {}
		cols = self.__dict__
		pattern = self._varPattern
		for k, v in cols.items(): #{
			if pattern.search(v): subs[k] = v
		#}
		changes = True
		while changes: #{
			changes = 0
			for k, v in cols.items(): #{
				val = v
				while True: #{
					R = pattern.search(v)
					if not R: break
					var = R.groups(1)[0]
					key = var.strip('{}')
					if key in cols: #{
						repl = cols[key]
						old = '$' + var
						v = v.replace(old, repl)
						continue
					#}
					break
				#}
				if val != v: #{
					changes += 1
					cols[k] = v
				#}
			#}
		#}
	#} expandvars
#} PostfixConfig

def MailInternet(*args): #{
	return Message(*args)
#} MailInternet

class MBOX(Csys.CSClass): #{
	_attributes = {
		'fname'		: None,
		'fh'		: None,
		'From'		: '',
		'mmdf'		: '',
	}
	def __init__(self, fname): #{
		Csys.CSClass.__init__(self)
		self.fname = fname
		if hasattr(fname, 'readline'):	fh = fname
		elif fname.endswith('.gz'):		fh = Csys.popen('zcat %s' % fname)
		elif fname.endswith('.bz2'):	fn = Csys.popen('bzcat %s' % fname)
		else:							fh = open(fname)
		self.fh = fh
		# Find initial 'From ' line.
		while True: #{
			line = fh.readline()
			if not line: return
			mmdf = self.mmdf
			if line.startswith('From '): #{
				if mmdf: line = line.replace(mmdf, '')
				self.From = line
				break
			#}
		#}
	#} __init__

	def nextMessage(self): #{
		'''Return next message from file'''
		lastline	= self.From
		if not lastline: return None
		msglines	= []
		fh			= self.fh
		mmdf		= self.mmdf
		line = True
		while line: #{
			line = fh.readline()
			if line: #{
				if mmdf: line = line.replace(mmdf, '')
				if line.startswith('From '): #{
					self.From = line
					break
				#}
				lastline = line
				msglines.append(line)
			#}
		#}
		else: #{ no break found so are at end of file
			self.From = None
			fh.close()
		#}
		if msglines: return MailInternet(''.join(msglines))
		return None
	#} nextMessage
#} class MBOX

class SendmailDirectError(Csys.Error): #{
	pass
#} SendmailDirectError

class SendmailDirect(Csys.CSClass): #{
	'''Send Message directly to domain server bypassing
	postfix, amavisd, and clamav.

	This will fall back to 127.0.0.1 if none of the MX servers
	for the domain are available so one must be sure that the
	inet_interfaces for postfix includes 127.0.0.1.
	'''
	_attributes = dict(
		toaddrs		= '',
		fromaddr	= '',
		domain		= '',
		msg			= '',
		verbose		= False,
		hostname	= '',
		_errors		= [],
	)
	def __init__(self, fromaddr, toaddrs, msg, **kwargs): #{
		'''
		Setting hostname will bypass the search for MX records.
		This will normally be done with localhost or 127.0.0.1.

		Setting domain will bypass splitting toaddr to get the
		destination domain for MX record search.
		'''
		Csys.CSClass.__init__(self, True, **kwargs)
		self.fromaddr	= fromaddr
		self.toaddrs	= toaddrs
		self.msg		= msg
		if not self.domain: #{
			try: #{{
				self.domain = toaddrs.split('@', 1)[1]
			#}
			except IndexError: #{
				self.domain = Csys.Config.hostname
			#}}
		#}
	#} __init__

	def sendmail(self): #{
		'''Send message directly to MX servers'''
		from Csys.DNS import dnsmx
		from smtplib import SMTP

		if self.hostname: #{{
			mxrecs = [self.hostname]
		#}
		else: #{
			mxrecs = dnsmx(self.domain, wantarray=True)
			mxrecs.sort()
			mxhosts = [mxrec.host for mxrec in mxrecs]
		#}}
		if not ('127.0.0.1' in mxhosts or 'localhost' in mxhosts): #{
			mxhosts.append('127.0.0.1')
		#}
		for host in mxhosts: #{{
			if self.verbose: print 'sendmail: trying >%s<' % host
			try: #{{
				server = SMTP(host)
				server.sendmail(
					self.fromaddr,
					self.toaddrs,
					self.msg,
				)
				server.quit()
				break
			#}
			except Exception, e: #{
				self._errors.append(str(e))
			#}}
		#}
		else: #{
			raise SendmailDirectError(
				'\n'.join(self._errors)
			)
		#}}
	#}
#} SendmailDirect

import email

from email.Generator import Generator
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
from email.MIMENonMultipart import MIMENonMultipart

class MIMEDataError(Csys.Error): #{
	pass
#} MIMEDataError

import string

_saltchars = string.letters + string.digits

def _mksalt(size=10): #{
	'''Return salt string from _saltchars set'''
	from random import randint
	if size < 2: raise Csys.Error('mksalt: size %d < 2' % size)
	n = len(_saltchars) - 1
	salt = ''
	while(size > 0): #{
		salt += _saltchars[randint(0, n)]
		size -= 1
	#}
	return salt
#} _mksalt

def makeMessageId(container): #{
	container['Message-Id'] = '%s@%s' % (_mksalt(20), Csys.Config.hostname)
	return container
#} makeMessageId

def newContainer(): #{
	boundary = _mksalt(20)
	container = MIMEBase('multipart', 'mixed', boundary=boundary)
	container['Date'] = rfcDate()
	makeMessageId(container)
	return container
#} newContainer

class MIMEData(MIMENonMultipart): #{
	'''Handle general MIME data using base64 encoding'''
	def __init__(self, ctype, csubtype, data=None, fname=None, **kw): #{
		'''Create a general MIME document, base64 encoded.

		data may be either a string containing the data, or
		an open file handle with a read method.
		
		fname is the file name that will be put in the name
		parameter of the MIME type.  If data is not specified,
		this file will be opened, its data read, and used.  The
		basename of this will be used for the part name.
		'''
		if not (data or fname): #{
			raise MIMEDataError('must specify data or fname')
		#}
		if data: #{{
			if hasattr(data, 'read'): #{
				data = data.read()
			#}
		#}
		else: #{
			data = open(fname).read()
		#}}
		if fname: #{
			if not 'name' in kw: kw['name'] = os.path.basename(fname)
		#}
		MIMENonMultipart.__init__(self, ctype, csubtype, **kw)
		self.set_payload(data)
		Encoders.encode_base64(self)
	#} __init__
#} class MIMEData

if __name__ == '__main__': #{
	print 'OK'
	_verbose = True
	# msg = MailInternet('/tmp/tmpmail')
	# print msg.firstReceived('whl.celestial.net').ip

	from cStringIO import StringIO

	container = newContainer()
	container['From'] = 'bill@mi.celestial.com'
	container['To'] = 'bill@mail.mi.celestial.com'
	container['Subject'] = 'testing mime parts'
	container['Date'] = rfcDate()
	container.attach(MIMEText('this is a test\n'))
	print 'md5: ', md5('this is a test').xdigest()
	f = StringIO()
	g = Generator(f, False)
	g.flatten(container)
	# f.seek(0)
	print f.getvalue()
	sys.exit(0)
	# the code below here is a sample
	container = newContainer()
	container['From'] = 'bill@mi.celestial.com'
	container['To'] = 'bill@mail.mi.celestial.com'
	container['Subject'] = 'testing mime parts'
	container['Date'] = rfcDate()
	intro = MIMEText(
		'This is a test.  This is only a test'
	)
	zipfile = 'RBTEST.zip'
	zippart = MIMEData('application', 'x-zip-compressed', fname=zipfile)
	container.attach(intro)
	container.attach(zippart)
	sendmail = '%s -t' % Csys.Config.sendmail
	f = StringIO()
	g = Generator(
		f, # Csys.popen(sendmail, 'w'),
		False
	)
	g.flatten(container)
	# f.seek(0)
	print f.getvalue()
#}
