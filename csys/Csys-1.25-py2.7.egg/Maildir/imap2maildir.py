#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/Maildir/imap2maildir.py,v 1.1 2007/10/06 00:14:35 csoftmgr Exp $
# $Date: 2007/10/06 00:14:35 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: imap2maildir.py,v 1.1 2007/10/06 00:14:35 csoftmgr Exp $
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

import imaplib
import Csys.Passwd
from Csys.MailInternet import MailInternet
import Csys.Maildir

_hasChildren	= re.compile('HasChildren')
_reFunnyChars	= re.compile(r'[^a-zA-Z0-9.]+')
_INBOX			= re.compile(r'^INBOX\.{0,1}')
# pattern to remove CRs from DOSish CRLF at end of lines.
CRLF			= re.compile(r'\r$', re.MULTILINE)
_namespaceRe	= re.compile(r'\({1,2}"([^"]*)"\s+"([^"]*)"\){1,2}')

class Namespace(Csys.CSClass): #{
	_attributes = {
		'prefix'	: 'INBOX.',
		'delim'		: '.',
	}
	def __init__(self, R): #{
		Csys.CSClass.__init__(self)
		self.prefix = R.group(1)
		self.delim	= R.group(2)
	#} __init__
#} Namespace

def getNamespaces(conn): #{
	'''Get namespaces from a connection'''
	namespaces = []
	try: #{{
		c, d = conn.namespace()
		print c, d
		if c != 'OK': return None
		d = d[0].replace(' NIL ', '')
		while d: #{
			R = _namespaceRe.search(d)
			if not R: break
			namespaces.append(Namespace(R))
			d = d[R.end():]
		#}
	#}
	except: raise #}
	namespaces = []
	return namespaces
#} getNamespaces

_FolderRe		= re.compile(
	r'^('			# start description (
	r'\([^)]+\)'	# parenthesised
	r')\s+"(.)"\s+"(.*)"$'
)

class Folder(Csys.CSClass): #{
	'''Folderish information'''
	_attributes = {
		'name'			: '',
		'delim'			: '.',
		'status'		: '',
		'haschildren'	: False,
		'name_courier'	: '',
	}
	def __init__(self, R): #{
		'''Get parts from regex match'''
		Csys.CSClass.__init__(self)
		self.status = R.group(1)
		if _hasChildren.search(self.status): self.haschildren = True
		self.delim	= R.group(2)
		self.name = R.group(3)
		name = self._INBOX.sub('', self.name)
		if name: #{{
			parts = []
			#
			# split into subfolders on delimiter then replace any
			# characters that aren't letters or numbers with an
			# underscore character.  Finally join on the Courier Imap
			# delimiter, '.'.
			#
			for part in self.name.split(self.delim): #{
				parts.append(self._reFunnyChars.sub('_', part))
			#}
			name = '.'.join(parts)
		#}
		else: name = None #}
		self.name_courier = name
	#} __init__

	def __cmp__(self, other): return cmp(self.name, other.name)
#} Folder

def getFolders(conn): #{
	'''Get folders from a connection'''
	c, data = conn.list()
	if c != 'OK': return None
	folders = []
	for d in data: #{
		# sys.stderr.write('%s\n' % d)
		R = _FolderRe.search(d)
		if R: #{
			# sys.stderr.write('matched\n')
			folders.append(Folder(R))
		#}
	#}
	return folders
#} getFolders

def imap2maildir(conn, user, password, localuser=None): #{
	'''Copy all mail from IMAP server to Maildir
	
	conn is an open connection to the IMAP server.
	user and password are those on the IMAP server.
	localuser is the user on the local system.
	'''
	if not localuser: localuser = user
	pw = Csys.Passwd.getpwnam(localuser)

	maildir = os.path.join(pw.home, 'Maildir')
	print maildir

	folders = getFolders(conn)
	folders.sort()
	for folder in folders: #{
		oldfolder = folder.name
		newfolder = folder.name_courier
		sys.stderr.write('oldfolder: %s\n' % oldfolder)

		c, set = conn.select(oldfolder)
		if c != 'OK': #{
			sys.stderr.write('cannot select %s\n' % oldfolder)
			continue
		#}
		c, set = conn.search(None, 'ALL')
		if c != 'OK': continue
		mbox = Csys.Maildir.getMaildir(
			maildir,
			newfolder,
			user=pw,
			dupsok = False,
		)
		msgnumbers = set[0].split()

		for msgnmbr in msgnumbers: #{
			c, data = conn.fetch(msgnmbr, '(RFC822)')
			if c != 'OK': continue
			# get rid of DOS line endings
			msg = CRLF.sub('', data[0][1])
			msg = MailInternet(msg)
			mbox.addmsg(msg)
		#}
	#}
	conn.logout()
#} imap2maildir

cfgFile = os.path.join(
	Csys.prefix, 'etc/csadmin',
	'imap2maildir.conf',
)
cfg = Csys.ConfigParser(cfgFile)
sections = cfg.sections()
sections.sort()

for section in sections: #{
	userCfg		= cfg.getDict(section, asClass=True)
	user		= section + userCfg.suffix
	password	= userCfg.password
	localuser	= userCfg.localuser or section
	if verbose: print user, password, localuser
	server		= userCfg.mailhost
	conn		= imaplib.IMAP4(server)
	print conn
	curServer = server

	try: c, d = conn.login(user, password)
	except: c = 'FAIL'

	if c != 'OK': #{
		sys.stderr.write(
			'imap2maildir: login failed user %s pw >%s<' %
			(user, password)
		)
		continue
	#}
	namespaces = getNamespaces(conn)
	if namespaces: #{
		for namespace in namespaces: #{
			print namespace.prefix, namespace.delim
		#}
		inbox = namespaces[0].prefix
	#}
	else: inbox = ''
	print 'here'
	if verbose: sys.stderr.write('inbox: >%s<\n' % inbox)
	imap2maildir(conn, user, password, localuser)
	conn.logout()
#}

