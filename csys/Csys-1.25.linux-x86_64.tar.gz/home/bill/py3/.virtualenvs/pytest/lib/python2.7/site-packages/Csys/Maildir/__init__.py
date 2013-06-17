# $Header: /vol/cscvs/python-Csys/Maildir/__init__.py,v 1.12 2013/06/11 19:56:14 csoftmgr Exp $
# $Date: 2013/06/11 19:56:14 $

import Csys, os, os.path, sys, re, time
import Csys.MailInternet

__doc__ = '''Celestial Software Maildir handling

$Id: __init__.py,v 1.12 2013/06/11 19:56:14 csoftmgr Exp $
'''

__version__='$Revision: 1.12 $'[11:-2]

import Csys.Passwd, ConfigParser
from Csys.Dates import getdate, today, DF_YYYY, DF_YYYYdMM, str2seconds

class DropMessage(Csys.Error): #{
	'''Raised when the mailbox rules return DROP'''
	def __init__(self, maildir, msg=''): #{
		self.maildir	= maildir
		self.mailbox	= maildir.mailbox
		self.msg		= msg
		Csys.Error.__init__(self, 'Message Dropped')
	#} __init__
#} DropMessage

# These are the Csys.Dates flags for archiving
_archiveDateFmts = {
	'week'	: DF_YYYYdMM,
	'month'	: DF_YYYYdMM,
	'year'	: DF_YYYY,
}

class MaildirFileName(Csys.CSClass): #{
	__doc__ = Csys.detab('''
	The MaildirFileName class breaks out the component parts of Maildir
	file names, time, sequence, host, and info.

	file = MaildirFileName(None, msg, mbox) returns the Maildir filename based on the
	contents of the MailInternet object msg.  The attribute file.fname will be undef
	if there's no valid file name (duplicates normally).  The filename is in the format:

	 $date.$md5body[_nnn].hostname[:info]

	The $date is normally the Unix date from the Date header, but may be
	the date in the first smail-3.2 Received: header if the str2time() fails.

	The md5 checksum is the middle field, optionally followed by a sequence number
	in the format '_%03d'.

	The system hostname is normally derived from the `hostname` program,
	but may be specified using the -hostname option to new.

	The optional status info is determined by looking at the Status and
	X-Status fields in the $msg header (mutt uses X-Status to indicate a
	message that has been replied to).

	After the file name has been built using these rules, the filename method next
	checks to see if the -nodupbody is true and if there's already a message with that
	checksum.  If these are true, it then returns undef.

	Next it checks to see if there's already a message with this file name in the
	mailbox.  If there is, and _dupsok is true it will then generate a sequence number
	to append to the $md5 checksum to get an unused file name, returning that name and
	time.

	If the file name exists, and _dupsok is false, it then checks to see if -dupmailbox
	has been defined.  If it has, then it forces dupsok in that mailbox, and returns
	the filename and time for that mailbox.

	If the file name exists, and neither _dupsok or _dupmailbox have been set, it
	returns undef for the file name.
	''')
	_attributes = {
		'fname'		: '',		# Full path name
		'basename'	: None,		# basename
		'utime'		: None,		# Unix time
		'md5'		: None,		# md5 sum of message body
		'seq'		: None,		# seqence
		'info'		: '',		# message status flags
		'mbox'		: None,		# Maildir parent
	}
	def __cmp__(self, other): #{
		return(
			cmp(
				(self.utime, self.md5, self.seq, self.info),
				(other.utime, other.md5, other.seq, other.info),
			)
		)
	#}
	_dateRE = re.compile(
		r'^(\w+,\s+\d{1,2}\s+\w+\s+)(\d{1,3})(\s+\d{1,2}:\d{1,2}:\d{1,2}.*)$'
	)
	def __init__(self, fname, msg=None, mbox=None): #{
		'''Break fname into components'''
		assert fname or msg, '%s: file name or message required' % self.__class__
		Csys.CSClass.__init__(self)
		if fname: #{
			self.fname = fname
			self.basename = basename = os.path.basename(fname)
			utime, seq, hostinfo = basename.split('.', 2)

			try: self.utime = long(utime) #{
			except: self.utime = os.stat(fname).st_mtime
			#}

			n = len(seq)

			if   n < 32:  self.seq = seq # too short to be md5 checksum
			elif n == 32: self.md5 = seq
			else: self.md5, self.seq = seq.split('_')

			hostparts = hostinfo.split(':', 1)
			self.hostname = hostparts.pop(0)
			if hostparts: self.info = hostparts[0]
			return
		#} end fname processing

		try: utime = msg.msgdate()
		except: utime = int(time.time())
		self.utime = utime
		self.md5	= msg.md5()
		if mbox.archive: #{
			datefmt = _archiveDateFmts.get(mbox.archive, DF_YYYYdMM)
			subfolder = today(self.utime, datefmt)
			topfolder = mbox.folder
			if topfolder is None: topfolder = mbox.folderprefix
			newfolder = '%s.%s' % (topfolder, subfolder)
			kwargs = self._kwargs.copy()
			kwargs['archive'] = None
			parent = getMaildir(mbox.mailbox, None)
			kwargs['shared'] = parent.shared
			mbox = getMaildir(mbox.mailbox, newfolder, **kwargs)
		#}
		self.mbox	= mbox
		maildirbox	= mbox._mailboxdir
		while True: #{
			self.hostname	= mbox.hostname
			uniq = "%09d.%s.%s" % ( self.utime, self.md5, self.hostname);
			# Truncate filename if it will exceed the RFC max length.
			if not mbox.shorthostname and len(uniq) > 70: #{
				mbox.shorthostname = True
				mbox.hostname = self.hostname[:self.hostname.find('.')]
				continue
			#}
			break
		#}
		# uniq is now set
		info = msg.get('Status', failobj='')
		if info: info = 'S'
		info += msg.get('X-Status', failobj='')
		if info: #{
			self.info = ':2,'
			for c in list(info): #{
				if c != ' ': self.info += c
			#}
		#}
		if self.info: uniq = os.path.join(maildirbox, 'cur', uniq + self.info)
		else: uniq = os.path.join(maildirbox, 'new', uniq)

		dupmd5 = mbox._hashmd5.get(self.md5)
		# print 'dupmd5: ', dupmd5
		if dupmd5: #{
			if mbox.lastdupbody: #{
				maxutime = self.utime
				for f in dupmd5: #{
					if long(os.path.basename(f).split('.')[0]) >= maxutime: #{
						mbox._hashmd5[self.md5] = [f]
						uniq = None
						break
					#}
					try: os.unlink(f)
					except: break
				#}
				else: #{
					# No break hit so all unlinks OK
					mbox._hashmd5[self.md5] = [] # empty array
				#}
			#}
			elif mbox.nodupbody: #{
				uniq = None
			#}
		#}
		if uniq: #{
			if os.access(uniq, os.F_OK): #{ # file exists
				if mbox.dupsok: #{{
					utime, md5, hostname = (self.utime, self.md5, mbox.hostname)
					seq = 1
					while True: #{
						uniq = "%s.%s_%03d.%s" % (utime, md5, seq, hostname)
						if info: uniq = os.path.join(maildirbox, 'cur', uniq + info)
						else:	 uniq = os.path.join(maildirbox, 'new', uniq)
						if not os.access(uniq, os.F_OK): break
						seq += 1
					#}
				#}
				elif mbox.dupmailbox: #{
					dupmailbox = mbox.dupmailbox
					kwargs = mbox._kwargs.copy()
					kwargs['user'] = mbox.user
					if re.match(r'^[~/]', dupmailbox): #{
						dupbox = getMaildir(dupmailbox, None, **kwargs)
					#}
					else: #{
						dupbox = getMaildir(mbox.mailbox, dupmailbox, **kwargs)
					#}
					dupbox.dupsok	= True # make sure it accepts duplicates
					fnameDup		= dupbox.filename(msg)
					uniq			= fnameDup.fname
					self.mbox		= fnameDup.mbox
					self.seq		= fnameDup.seq
				#}
				else: uniq = None #}
			#}
		#}
		self.fname = uniq

		if uniq: self.dirname, self.basename = os.path.split(uniq)
		else: self.basename = None
	#} __init__

	def __str__(self): return self.fname

	def get_attributes(self): #{
		'''return tuple(utime, md5, seq, hostname, info)'''
		return (tuple(self.utime, self.md5, self.seq, self.hostname, self.info))
	#} getAttributes

#} class MaildirFileName

_MaildirIndex = {} # dictionary of Maildir instances

_MailRulesIndex = {} # dictionary of Mailrules lists

class Maildir(Csys.CSClass): #{
	debugOut = [time.ctime(time.time())]
	_attributes = {
		'mailbox'		: '',		# mailbox directory
		'folder'		: None,		# folder in mailbox
		'archive'		: None,		# Archive by year or month
		'dupmailbox'	: None,		# mailbox object for duplicates
		'debug'			: False,	# True for debugging output
		'dupsok'		: False,	# duplicate messages OK
		'hostname'		: Csys.Config.hostname_short,
		'lastdupbody'	: False,	# save last dup body
		'mailrules'		: [],		# header, pattern, folder files
		'nocreate'		: False,	# true to prevent mailbox creation.
		'nodupbody'		: False,	# duplicate MD5 bodies not allowed
		'nohashes'		: False,	# don't build hash tables.
		'folderprefix'	: 'INBOX',	# mailbox prefix
		'shared'		: False,	# shared folders have different permissions
		'readonly'		: False,	# Shared only
		'sa_check'		: True,
		'sa_host'		: 'localhost',
		'sa_port'		: 783,
		'sa_levels'		: ((20.0, 'DROP'),(5.0, 'spam')),
		'sa_subject_prefix' : '***SPAM***',
		'shorthostname'	: True,		# set TRUE to use short hostname
		'smtphost'		: 'localhost',	# outgoing SMTP server
		'smtpport'		: 25,		# output SMTP port
		'vacation_allow': True,		# Allow vacation messages
		# 'myorigin'		: Csys.MailInternet.PostfixConfig().myorigin,
		'taggedboxes'	: False,	# Set true for deliver processing
		'user'			: None,		# username or User::pwent object
		'verbose'		: False,	# verbose output
		'_cfg'			: None,		# ConfigParser instance
		'_configfiles'	: [os.path.join(Csys.prefix, 'etc/csbase/Maildir.conf')],
		'_foldermaps'	: {},		# map of folders
		'_maildirs'		: {},		# map of folders to Maildirs (shared)
		'_hashmd5'		: {},		# hash of existing MD5 checksums
		'_mailboxdir'	: None,		# top destination (mailbox + '.' + folder)
		'folderdir'		: None,     # public version of _mailboxdir
		'_mailboxes'	: [],		# mailbox directory names
		'_newtime'		: -1,		# last time checked for newest
		'_parentmbox'	: None,		# Parent box if this is a folder
		'_permsdir'		: 0700,		# Mail directory perms
		'_permsfile'	: 0600,		# File permissions
		'_lastfilename' : None,		# last file name looked up
		'cronarchive'	: '',		# may be set for cron archives of folder
		'xelmretry'		: 60,		# seconds for Xelm rescan
		'junkfolder'	: 'spam.missed', # drop folder for spam
		'falsepositive'	: 'spam.falsepositive', # drop folder for FPs.
		'whitelist'		: 'spam.whitelist',
		'whitelistsave'	: '',		# set to save whitelisted files
		'purgetime'		: '',		# set to seconds to hold
	}
	_skipAttrCopy = (
		'mailbox',
		'folder',
		'_cfg',
		'_configfiles',
		'_foldermaps',
		'_maildirs',
		'_hashmd5',
		'_mailboxdir',
		'folderdir',
		'_mailboxes',
		'_newtime',
		'_parentmbox',
		'_lastfilename',
	)
	_booleanOptions = (
		'debug',
		'dupsok',
		'lastdupbody',
		'nocreate',
		'nodupbody',
		'nohashes',
		'sa_check',
		'shared',
		'shorthostname',
		'taggedboxes',
		'verbose',
		'vacation_allow',
	)
	_listOptions = (
		'mailrules',
	)
	# these hashes should have no defaults, and will be stripped of all keys
	# in the _parseDefaults routine below.
	_noDefaults = (
		'foldermaps',
		'maildirs',
	)
	def __init__(self, mailbox, folder=None, **kwargs): #{
		'''Create Maildir instance'''
		Csys.CSClass.__init__(self, **kwargs)

		# this should have been expanded in getMaildir so we won't worry
		# about expanding ``~[username]/directory'' and user options.
		self.mailbox	= mailbox

		global _MaildirIndex

		# map this early (and often)
		_MaildirIndex[(mailbox, folder)] = self

		if folder: #{
			if folder == 'DROP': raise DropMessage(self)

			# make sure there's a top level Maildir
			parent = getMaildir(mailbox, None, **kwargs)
			mailbox = parent._maildirs.get(folder, parent.mailbox)
			if mailbox != self.mailbox: #{
				self.mailbox = mailbox
				parent = getMaildir(mailbox, None, **kwargs)
			#}
			folder = parent._folderRemovePrefix(folder)
			_MaildirIndex[(mailbox, folder)] = self
			if folder: folder = parent._foldermaps.get(folder.lower(), folder)
			_MaildirIndex[(mailbox, folder)] = self
		#}
		_MaildirIndex[(mailbox, folder)] = self
		if folder: #{
			folder = parent._foldermaps.get(folder.lower(), folder)
			mailbox = parent._maildirs.get(folder, parent.mailbox)

			folders = folder.split('.')

			folders.pop()
			if folders: dirfolder = '.'.join(folders)
			else: dirfolder = None

			# This will insure that the top level mailbox exists
			if mailbox != self.mailbox: getMaildir(mailbox, None, **kwargs)

			# This will recursively get the parents.
			parent = self._parent = getMaildir(mailbox, dirfolder, **kwargs)
			folder = parent._folderRemovePrefix(folder)
			if not folder is None: folder = parent._foldermaps.get(folder.lower(), folder)
			mailbox = parent._maildirs.get(folder, parent.mailbox)
			cols = self.__dict__
			# this inherits the parent's attributes
			for key, val in parent.__dict__.items(): #{
				if not key in self._skipAttrCopy: cols[key] = val
			#}
			_MaildirIndex[(mailbox, folder)] = self
			if folder is None: #{
				folder = self.folderprefix
				_MaildirIndex[(mailbox, folder)] = self
			#}
			self.mailbox = mailbox
			self.folder = folder
			self._parent = parent
		#}
		_MaildirIndex[(mailbox, folder)] = self
		if self.shorthostname and self.hostname.find('.') != -1: #{
			self.hostname = self.hostname[:self.hostname.find('.')]
		#}
		if os.geteuid() != 0 or not self.user: self.user = os.environ['USER']
		if not isinstance(self.user, Csys.Passwd.Passwd): #{
			self.user = Csys.Passwd.getpwnam(self.user)
		#}
		# This should never be true at this point.
		self._expandmailbox()
		self._mailboxdir = self.mailbox
		mailbox_conf = (self.mailbox + '.conf')
		if not mailbox_conf in self._configfiles:
			self._configfiles.append(mailbox_conf)

		if not os.path.exists(mailbox_conf): #{
			# Create missing maildir configuration files from prototypes
			newmode = 0600
			if os.path.basename(self.mailbox) == 'Maildir': #{
				configfile = self._configfiles[0]
				Csys.copyfile(configfile, mailbox_conf, self.user, newmode)
			#}
			else: #{
				configfile	= os.path.join(Csys.prefix, 'etc/csbase/MaildirShared.conf')
				fhInput		= open(configfile)
				fhOutput	= Csys.openOut(mailbox_conf, user=self.user, mode=newmode)
				for line in fhInput: #{
					if line.startswith('folderprefix'):
						fhOutput.write('folderprefix = %s\n' % self.folderprefix)
					else:
						fhOutput.write(line)
				#}
				fhInput.close(); fhOutput.close()
			#}
		#}
		self._mailbox_conf = mailbox_conf
		self._parseDefaults(kwargs)
		if self.folder and self.folder != self.folderprefix: #{
			self._mailboxdir = os.path.join(self.mailbox, '.' + self.folder)
			self.folderdir = self._mailboxdir
		#}
		else: #{
			self._mailboxdir = self.folderdir = self.mailbox
		#}
		if self.shared: #{
			self._permsdir	= 0755
			self._permsfile	= 0644
		#}
		self._mkmailbox()
	#} __init__

	def _folderRemovePrefix(self, folder): #{
		'''Remove leading prefix from folder'''
		assert type(folder) == type(''), 'folder is not string'
		debug = self.debug
		debug = False
		# folder = folder[:]
		if folder: #{
			folder = folder.replace('/', '.')
			parts = folder.split('.', 1)
			if parts[0] == self.folderprefix: #{
				try: folder = parts[1]
				except: folder = None
			#}
		#}
		return folder
	#} _folderRemovePrefix

	def _parseDefaults(self, kwargs): #{
		'''Parse user's $HOME/Maildir.conf file if present
		
		The configuration file should have a rule for INBOX if the defaults
		for that are different than in the DEFAULT section.  Subfolders of
		the INBOX should *NOT* have ``INBOX.'' in the prefix, but just be
		the folder name.  All shared folders should be under the user's
		$HOME/MaildirShared directory.  The main folder will be in the
		public, and subfolders as ``public.folder''
		'''
		if self.user is None: #{
			self.user = Csys.Passwd.getpwnam(os.environ['USER'])
		#}
		mailbox		= self.mailbox
		self._cfg = cfg = ConfigParser.ConfigParser()
		configsread = cfg.read(self._configfiles)
		try: #{{
			defaults = cfg.defaults()
			defaultKeys = defaults.keys()
		#}
		except: #{
			defaultKeys = ()
		#}}
		folder = self.folder # already mapped above

		cols = self.__dict__
		if folder is None: folder = self.folderprefix
		#
		# This gets the section, inheriting from parent folders or
		# getting from the the defaults if there are no parents.
		#
		folderparts = folder.split('.')
		section = folder
		while folderparts: #{{
			section = '.'.join(folderparts)
			if cfg.has_section(section): #{
				args = dict(cfg.items(section))
				break
			#}
			folderparts.pop()
		#}
		else: #{
			args = defaults
			section = 'DEFAULT'
		#}}
		# we don't want to inherit this
		try: del args['mailbox']
		except: pass

		for key, val in args.items(): #{
			if key in cols and not key in kwargs: #{
				if key in self._booleanOptions: #{{
					cols[key] = cfg.getboolean(section, key)
				#}
				elif key in self._listOptions: #{
					cols[key] = Csys.grep('.',
						Csys.COMMA_SPACES.split(cfg.get(section, key))
					)
				#}
				else: #{
					val = val.strip(''''"''')
					testval = val.lower()
					# simple boolean tests for things that might
					# be character variables.
					if testval in ('true', 'yes', 'on'): val = True
					elif testval == ('false', 'no', 'off'): val = False
					cols[key] = val
				#}}
			#}
		#}
		for attr in self._noDefaults: #{
			try: d = dict(cfg.items(attr)) #{
			except: continue #}

			rec = self.__dict__['_%s' % attr]
			rec.update(d)
			Csys.delSlice(defaultKeys, rec)
		#}
		if isinstance(self.sa_levels, basestring): #{
			l = self.sa_levels.strip().split()
			sa_levels = []
			try: #{{
				for i in range(0, len(l), 2): #{
					sa_levels.append( (float(l[i]), l[i+1]) )
				#}
				sa_levels.sort()
				sa_levels.reverse()
				self.sa_levels = tuple(sa_levels)
			#}
			except: #{
				self.sa_levels = ((20.0, 'DROP'),(5.0, 'spam'))
			#}}
		#}
		self._expandmailbox()
		# self.dumpAttrs()
	#} _parseDefaults

	def _expandmailbox(self): #{
		'''Expand mailbox path if it starts with ``~'' '''
		global _MaildirIndex

		mailbox = self.mailbox
		if mailbox.startswith('~'): #{
			if self.user is None: #{
				self.user = Csys.Passwd.getpwnam(os.environ['USER'])
			#}
			user, dir = mailbox[1:].split('/')
			if user: #{
				user = Csys.Passwd.getpwnam(user)
				self.user = user
			#}
			self.mailbox = os.path.join(self.user.home, dir)
			_MaildirIndex[(self.mailbox, self.folder)] = self
		#}
	#} _expandmailbox

	def _mkmailbox(self): #{
		'''Create mailbox if necessary

		mkmailbox checks the specified mailbox, creating directories if
		necessary unless the nocreate option to new is true.  If nodupbody is
		true, it also builds the md5 hash to allow identification of duplicate
		mail bodies (which requires parsing all files in the directories to get
		the checksums so can be fairly time consuming on large mailboxes).

		It returns self normally, and None if any mailbox directory doesn't
		exist.'''

		mbox = self._mailboxdir
		# print mbox
		self._mailboxes = mailboxes = (
			mbox,
			os.path.join(mbox, 'cur'),
			os.path.join(mbox, 'new'),
			os.path.join(mbox, 'tmp'),
		)
		perms = self._permsdir # shared taken care of __init__

		if self.user: uid, gid = self.user.uid, self.user.gid
		else: uid = gid = None

		for dir in mailboxes: #{
			if not os.path.isdir(dir): #{
				if self.nocreate: return None
				Csys.mkpath(dir, perms, uid, gid)
				# if self.user: os.chown(dir, self.user.uid, self.user.gid)
			#}
			if self.shared: #{
				if self.readonly: perms = 0755
				else: perms = 01777
			#}
		#}
		if (self.nodupbody or self.lastdupbody) and not self.nohashes:
			self._set_hashmd5()
		return self
	#} _mkmailbox

	def _add_hashmd5(self, fname, md5=None): #{
		'''Add fname to md5 table, creating if necessary'''
		if md5 is None: md5 = MaildirFileName(fname).md5
		# print '_add_hashmd5(%s, %s)' % (fname, md5)
		if not md5 in self._hashmd5: self._hashmd5[md5] = []
		self._hashmd5[md5].append(fname)
	#} _add_hashmd5

	def _set_hashmd5(self, fname=None): #{
		'''Create md5 hash index if fname == None or add'''
		if fname: #{
			self._add_hashmd5(fname)
		#}
		else: #{
			mailbox = self._mailboxdir
			for subdir in ('cur', 'new'): #{
				dir = os.path.join(mailbox, subdir)
				for fname in os.listdir(dir): #{
					self._add_hashmd5(os.path.join(dir, fname))
				#}
			#}
		#}
	#} _set_hashmd5

	def _get_attributes(self, fname): #{
		'''Split fname into parts'''
		return(MaildirFileName(fname).get_attributes())
	#} _get_attributes

	_skip_hdrs = {
		# U.W. Imapd internal marker message
		'Subject' :
			re.compile("DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA"),
	}
	def addmsg(self, msg): #{
		'''Add message to Maildir'''
		# These are regular expressions to match for messages that should
		# be skipped.
		#
		if not isinstance(msg, Csys.MailInternet.Message): #{
			# hopefully this will convert anything necessary
			msg = Csys.MailInternet.Message(msg)
		#}
		for hdr, regex in self._skip_hdrs.items(): #{
			if msg.grep(hdr, regex, True): return None
		#}
		# fileObj = MaildirFileName(None, msg, self)
		self._lastfilename = fileObj = self.filename(msg)
		fname	= fileObj.fname
		if fname: #{
			mbox	= fileObj.mbox # may not be the same if dups allowed
			utime	= fileObj.utime
			self._add_hashmd5(fname, fileObj.md5)
			dir, file = os.path.split(fname)
			# the dirname below removes the subdirectory name
			tfile = os.path.join(os.path.dirname(dir), 'tmp', file)
			msg.delete('Content-Length')
			msg.delete('Lines')
			body = msg.bodystr.split('\n')
			msg.add('Content-Length', len(msg.bodystr))
			msg.add('Lines', len(body) - 1) # I'm not sure why this need to subtract one
			fh = open(tfile, 'wb')
			msg.print_msg(fh)
			fh.close()
			try: #{
				os.rename(tfile, fname)
				if self.user: os.chown(fname, self.user.uid, self.user.gid)
				os.utime(fname, (utime, utime))
				os.chmod(fname, self._permsfile)
			except: #{
				self.pushDebug('os.rename(%s, %s) failed' % (tfile, fname))
				raise
			#}}
		#}
		return self._lastfilename
	#} addmsg

	def newest(self, lasttime=0): #{
		'''Return newest time in the unread (new) directory'''
		__doc__ = Csys.detab('''
			mbox.newest() returns the time of the newest message in the
			Maildir new directory, or zero if the directory is empty.
			This may be used by ``biff'' type programs to determine
			whether new messages have arrived by comparing the date
			returned with the previous value.

			This method compares the modification time of the new
			directory with the newtime value stored that last time it
			was called, searching the directory only if it's been
			modified since the last call.  This information is available
			using the mbox.newtime() method;
		''')
		dir = os.path.join(self._mailboxdir, 'new')
		dirtime = os.stat(dir).st_mtime
		if dirtime > self._newtime: #{
			self._newtime = dirtime
			files = os.listdir(dir)
			if not files: return 0
			for file in files: #{
				time = MaildirFileName(file).utime
				if lasttime < time <= dirtime: lasttime = time
			#}
		#}
		return lasttime
	#} newest

	def filename(self, msg): #{
		'''Generate File name'''
		rc = self._lastfilename = MaildirFileName(None, msg, self)
		return rc
	#} filename

	def checkRules(self, msg, addmsg=False, do_sa_check=True): #{
		'''Check MailInternet message against rules returning Maildir
		
		It returns an MaildirFileName object which has all the
		relevant information on the filename including a maildir
		reference, utime, etc.

		If addmsg is True, the message will be added to the maildir.
		'''
		maildir = self
		user = self.user
		self.pushDebug('taggedboxes = %s' % Csys.printbool(self.taggedboxes))
		if self.taggedboxes: #{
			# the pattern will include the username to distinguish between
			# Delivered-To: patterns.
			pattern = re.compile(r'\b%s\+([-._a-zA-Z0-9]+)\@' % self.user.user)
			hdr = msg.grep('Delivered-To', pattern)
			if hdr: #{
				self.pushDebug('Delivered-To = %s' % hdr[0])
				R = pattern.search(hdr[0])
				folder = R.group(1).lower()
				# collapse multiple '.' to single '.'
				folder = re.sub(r'\.+', '.', folder)
				self.pushDebug('tag folder = %s' % folder)
				kwargs = self._kwargs.copy()
				kwargs['user'] = user
				maildir = getMaildir(self.mailbox, folder, **kwargs)
				folder = maildir.folder # this may have been mapped
			#}
		#}
		for mailrules in maildir.mailrules: #{
			mailrules = Csys.expanduser(mailrules, user)
			# We're caching the mailrules so that we don't have to be
			# continusly going back to the file to get the
			# rules.  The downside of this is that if one is
			# doing an extensive job (e.g. mbox2maildir), it
			# won't update during the run.
			rules = _MailRulesIndex.get(mailrules)
			if rules is None: #{
				try:
					fh = open(mailrules)
					rules = tuple(Csys.rmComments(fh, wantarray=True))
					fh.close()
				except: rules = tuple(())
				_MailRulesIndex[mailrules] = rules
			#}
			lineNumber = 0
			for line in rules: #{
				lineNumber += 1
				if not line: continue
				parts = [ x.strip() for x in line.split(':') ]
				if len(parts) < 3: continue
				hdrs = parts.pop(0) # same as shift
				folder = parts.pop(len(parts) - 1)
				pattern = ':'.join(parts)
				if msg.grep(hdrs, pattern, True): #{
					if folder == 'DROP': #{
						raise DropMessage(maildir, 'pattern >%s<' % pattern)
					#}
					msg.add('X-Csys-Mailrules',
						'%d (%s)' % (lineNumber, line.strip())
					)
					if folder.find('@') != -1: #{
						self._forward(msg, folder)
						continue
					#}
					kwargs = self._kwargs.copy()
					kwargs['user'] = user
					maildir = getMaildir(maildir.mailbox, folder, **kwargs)
					break
				#}
			#}
		#}
		if do_sa_check and maildir.sa_check: #{
			# SpamAssassin check -- presumably no SA headers redirected
			# this already.

			try: #{
				msg.checkSpamAssassin(
					maildir.user.user,
					maildir.sa_host,
					maildir.sa_port,
					maildir.sa_subject_prefix,
				)
			except: msg.sa_spam = False #}

			if msg.sa_spam : #{
				sa_score = msg.sa_score
				for level, spamfolder in maildir.sa_levels: #{
					if sa_score >= level: #{
						folder = spamfolder
						if folder == 'DROP': raise DropMessage(
							maildir, 'spam level %.2f' % sa_score
						)
						break
					#}
				#}
				else: folder = 'spam' # no break hit

				kwargs = self._kwargs.copy()
				kwargs['user'] = maildir.user
				maildir = getMaildir(maildir.mailbox, folder, **kwargs)
			#}
		#}
		if addmsg: #{{
			# check for existence of user's $HOME/.csforward file.
			if not msg.sa_spam: #{
				user = maildir.user
				csforward = os.path.join(user.home, '.csforward')
				maildir.pushDebug('checking %s' % csforward)
				if os.path.isfile(csforward): #{
					maildir.pushDebug('found %s' % csforward)
					s = os.stat(csforward)
					if s.st_uid != user.uid: #{
						maildir.pushDebug('csforward: %s not owned by %s' %
							(csforward, user.user)
						)
					#}
					elif (s.st_mode & 077): #{ # readable or writeable by other
						maildir.pushDebug(
							'csforward: %s incorect mode' % csforward
						)
					#}
					else: #{
						from email.Utils import parseaddr
						try: #{{
							fh = open(csforward)
							addr = parseaddr(fh.readline().strip())[1]
							self._forward(msg, addr)
							maildir.pushDebug('msg forwarded to %s' % addr)
							return None
						#}
						except: pass #}
					#}
				#}
			#}
			fileobject = maildir.addmsg(msg)
			if fileobject and fileobject.mbox: #{
				maildir = fileobject.mbox
				mailbox, folder = maildir.mailbox, maildir.folder
				if maildir.debug: #{
					if not folder: folder = 'None'
					errmsg = 'adding mailbox to ' + mailbox + ' ' + folder
					maildir.pushDebug(errmsg)
					failobj = '(None)'
					maildir.pushDebug('Subject: %s' % msg.get('Subject', failobj=failobj))
					maildir.pushDebug('Message-Id: %s' % msg.get('Message-Id', failobj=failobj))
				#}
			#}
			if maildir.vacation_allow: #{
				user = maildir.user
				vacation_msg = os.path.join(user.home, '.vacation.msg')
				if os.path.exists(vacation_msg): #{
					try: #{{
						s = os.stat(vacation_msg)
						if s.st_size > 0: #{
							vacation = 'vacation %s' % user.user
							try: #{
								fh = Csys.popen(vacation, 'w')
								fh.write(str(msg))
								fh.close()
							except: pass
							#}
						#}
					#}
					except Exception, e: #{
						maildir.pushDebug('Subject: %s' % msg.get('Subject', failobj=failobj))
						maildir.pushDebug('Message-Id: %s' % msg.get('Message-Id', failobj=failobj))
						maildir.pushDebug('Vacation Error: %s' % e)
					#}}
				#}
			#}
		#}
		else: #{
			# This is a minimal check that will return the
			# MaildirFileName object that addmsg would have used.
			for hdr, regex in self._skip_hdrs.items(): #{
				if msg.grep(hdr, regex, True): return None
			#}
			fileobject = MaildirFileName(None, msg, maildir)
		#}}
		return fileobject
	#} checkRules

	def _forward(self, msg, toAddress): #{
		'''Forward e-mail message to toAddress'''
		import smtplib
		msgid = msg.get('message-id')
		try: #{
			smtp = smtplib.SMTP(self.smtphost, self.smtpport)
			fromAddr = msg.sender
			smtp.sendmail(fromAddr, toAddress, str(msg))
		except smtplib.SMTPSenderRefused, err:
			self.pushDebug('Message Sender %s Refused' % fromAddr)
		except smtplib.SMTPRecipientsRefused, err:
			self.pushDebug('Message recipient %s Refused' % toAddress)
		except smtplib.SMTPDataError:
			self.pushDebug('Message Data Error Message-ID >%s<', msgid)
		except:
			self.pushDebug('Unknown SMTP error from >%s< to >%s< msgid' %
				(fromAddr, toAddress, msgid)
			)
		else:
			self.pushDebug('Message >%s< forwarded from >%s< to >%s<' %
				(msgid, fromAddr, toAddress)
			)
		#}
	#} _forward

	def pushDebug(self, msg): #{
		'''Add message to global debugOut list'''
		Maildir.debugOut.append(msg)
	#} pushDebug
	
	def getDebug(self): #{
		'''Return debug list'''
		return self.debugOut
	#} getDebug

	def getfilelist(self, sorted=False, mailobj=False, leq=None): #{
		'''Get list of files from cur and new directories'''
		files = []
		if not leq is None and isinstance(leq, basestring): #{
			try: leq = str2seconds(leq)
			except: leq = None
		#}
		for dir in ('cur', 'new'): #{
			dir = os.path.join(self.folderdir, dir) #{
			for file in os.listdir(dir): #{
				file = os.path.join(dir, file)
				if mailobj or leq: #{
					fobj = MaildirFileName(file)
					if leq and fobj.utime > leq: continue
				#}
				if mailobj: files.append(fobj)
				else: files.append(file)
			#}
		#}
		if sorted and files: files.sort()
		return files
	#} getfilelist

#} class Maildir

def getMaildir(mailbox, folder=None, **kwargs): #{
	'''Retrieve current Maildir or generate a new instance'''

	# Expand mailbox path if it starts with ``~''
	if mailbox.startswith('~'): #{
		user, dir = mailbox[1:].split('/')
		if not user: user = kwargs.get('user', os.environ['USER'])
		
		if not isinstance(user, Csys.Passwd.Passwd): #{
			kwargs['user'] = user = Csys.Passwd.getpwnam(user)
		#}
		mailbox = os.path.join(user.home, dir)
	#}
	return(_MaildirIndex.get((mailbox,folder), Maildir(mailbox, folder, **kwargs)))

#} getMaildir


def clearMaildirs(): #{
	'''Clear internal dictionary of Maildirs'''
	_MaildirIndex.clear()
#} clearMaildirs

def checkRules(maildir, msg, addmsg=False): #{
	'''Parse message against maildir.mailrules returning the proper maildir

	This may return strings, 'DROP' or an e-mail address so checking the
	output may be useful
	'''
	return (maildir.checkRules(msg, addmsg))
#}

if __name__ == '__main__': #{
	maildir = Maildir(os.path.expanduser('~/Maildir'))
	for mailrules in maildir.mailrules: #{
		print os.path.expanduser(mailrules)
	#}
	print 'OK'
#}
