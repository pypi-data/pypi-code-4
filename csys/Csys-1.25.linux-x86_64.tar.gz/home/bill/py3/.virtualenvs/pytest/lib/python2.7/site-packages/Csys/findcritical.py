#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/findcritical.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
# $Date: 2009/11/25 01:44:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Find Critical files

usage: %s [options] [dir [dir]]''' % Csys.Config.progname

__doc__ += '''

$Id: findcritical.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

	parser.add_option('-b', '--backup',
		action='store_true', dest='backup', default=False,
		help='Crate files for backups',
	)
	parser.add_option('-o', '--oldfiles',
		action='store_true', dest='oldfiles', default=False,
		help='Convert old findcritical databases',
	)
	parser.add_option('-r', '--remove',
		action='store_true', dest='remove', default=False,
		help='Remove missing files',
	)
	parser.add_option('-R', '--realpath',
		action='store_true', dest='realpath', default=False,
		help='Recalculate realpath for symlinks',
	)
	parser.add_option('-t', '--table',
		action='store_true', dest='table', default=False,
		help='Show missing files',
	)
	parser.add_option('-x', '--extract',
		action='store_true', dest='extract', default=False,
		help='Extract data to ascii',
	)
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

tripwiredir = os.path.join(Csys.prefix, 'var/tripwire')

if verbose: print 'tripwiredir >%s<' % tripwiredir

files = dict(
	symlinks	= os.path.join(tripwiredir, 'symlinks.db'),
	rhosts		= os.path.join(tripwiredir, 'rhosts.db'),
	setuids		= os.path.join(tripwiredir, 'setuids.db'),
	exclusions	= os.path.join(Csys.prefix, 'etc/csbase/exclusions'),
	ignore		= os.path.join(tripwiredir, 'tw.ignore'),
)
import anydbm
import bsddb
import Csys.SysUtils
sys.path.append(os.path.join(Csys.prefix, 'sbin'))

FileInfo = Csys.FileInfo

if options.oldfiles: #{
	oldfiles = dict(
		symlinks	= os.path.join(tripwiredir, 'symlinks.gdbm'),
		rhosts		= os.path.join(tripwiredir, 'rhosts.gdbm'),
		setuids		= os.path.join(tripwiredir, 'setuids.gdbm'),
	)
	for key in ('symlinks', 'rhosts', 'setuids'): #{
		oldfile = oldfiles[key]
		newfile	= files[key]
		if os.path.exists(oldfile) and not os.path.exists(newfile): #{
			# print key, oldfile, newfile
			dbold = anydbm.open(oldfile, 'r')
			dbnew = bsddb.btopen(newfile, 'c', 0600)
			key = dbold.firstkey()
			while(key): #{
				dbnew[key] = dbold[key]
				key = dbold.nextkey(key)
			#}
		#}
	#}
#}
files = Csys.CSClassDict(files)

os.chdir('/')
exclusions = [
	r'^/backups/',
	r'^/\.aw',
	r'^/\.autofsck',
	r'^/\.automount',
	r'^/\.autorelabel',
	r'^/etc/[uw]tmp',
	r'^/tmp/',
	r'^/net',
	r'^/tmp_mnt',
	r'^/usr/spool/uucp/L',
	r'^/var/spool/uucp/L',
	r'^/usr/spool/mail/',
	r'^/var/spool/mail/',
	r'^/var/spool/postfix/',
	r'^/usr/spool/postfix/',
	r'^/usr/spool/smail/',
	r'^/var/spool/smail/',
	r'^/usr/lib/news/L',
	r'^/var/log/',
	r'^/var/lock/',
	r'^/dev/',
	r'/Maildirs*/.*/new/',
	r'/log/main/',	# djbdns log files
	r'^/var/run/.*pid$',
	r'/supervise/status$',
	r'/\.[^/]*\.swp$',	# gvim swap files
	r'/etc/ioctl.save$',
	r'/etc/rmtab$',
	r'/etc/ssh_random_seed$',
	r'/csbackup/\d+/',	# cs backup directories
] # exclusions

mount_points = Csys.SysUtils.mounted(skip_prefix=None)
allMounted = Csys.SysUtils.getMounted()

if verbose: print 'mount_points: ' , mount_points
spool_dirs = Csys.SysUtils.spool_dirs(
	r'/postfix$|/s*mail$|/news$|/uucp$', mount_points
);
spool_dirs.extend([
	os.path.join(Csys.prefix, 'var/postfix'),
	os.path.join(Csys.prefix, 'var/uucp'),
	os.path.join(Csys.prefix, 'var/hylafax'),
])
if verbose: print 'spool_dirs: ', spool_dirs
exclusions.extend(['^%s' % x for x in spool_dirs])

if verbose: print 'exclusions: ', exclusions

def getExclusions(fname, exclusions=[]): #{
	if os.path.exists(fname): #{
		fh = open(fname)
		for line in Csys.rmComments(fh, wantarray=True): #{
			if line: #{
				pattern = '|'.join(exclusions)
				if not exclusions or not re.search(pattern, line): #{
					re.compile(pattern)
					exclusions.append(line)
				#}
			#}
		#}
	#}
	return exclusions
#} getExclusions

exclusions = getExclusions(files.exclusions, exclusions)

dbs = Csys.CSClassDict(dict(
	symlinks	= bsddb.btopen(files.symlinks, 'c', 0600),
	setuids		= bsddb.btopen(files.setuids, 'c', 0600),
	rhosts		= bsddb.btopen(files.rhosts, 'c', 0600),
))
if options.remove or options.table: #{
	def deletedbs(db, delete_list): #{
		for key in delete_list.keys(): del db[key]
		delete_list.clear()
	#} deletedbs

	if verbose: print "checking %s" % files.symlinks

	db = dbs.symlinks
	changed = False
	delete_list = {}

	quotePattern = re.compile(r'^"(.*)"$')
	spacePattern = re.compile(r'\s')
	for key, val in db.iteritems(): #{
		path = key[1:]
		# This will delete any files from the symlinks database
		# that contain whitespace that are not enclosed in double
		# quotes.
		if spacePattern.search(path): #{
			R = quotePattern.match(path)
			if R: #{{
				path = R.group(1)
			#}
			else: #{
				# Delete the old unquoted entry and add it back
				# with quotes.
				delete_list[key] = True
				key = '!"%s"' % path
				db[key] = val
				changed = True
			#}}
		#}
		R = quotePattern.match(path)
		if R: path = R.group(1)
		try: #{{
			obj = FileInfo(path, calcsums = False)
		#}
		except: #{
			if verbose: print '%s missing' % path
			delete_list[key] = True
			changed = True
			continue
		#}}
		if not obj.islink: #{
			print '%s is not a link' % path
			delete_list[key] = True
			changed = True
		#}
		if options.realpath: #{
			ln = '# ln -s %s %s' % (
				repr(os.path.realpath(path)),
				repr(path),
			)
			db[key] = ln
			changed = True
		#}
	#}
	if options.remove and delete_list: deletedbs(db, delete_list)

	if verbose: print "checking %s" % files.setuids

	db = dbs.setuids
	changed = False

	for key, val in db.iteritems(): #{
		path = key
		R = quotePattern.search(path)
		if R: path = R.group(1)
		try: #{{
			obj = FileInfo(path, calcsums=True)
		#}
		except: #{
			delete_list[key] = True
			continue
		#}}
		if not obj.suid: #{
			delete_list[key] = True
		#}
	#}
	if options.remove and delete_list: deletedbs(db, delete_list)

	if verbose: print "checking %s" % files.rhosts

	db = dbs.rhosts
	changed = False

	for key, val in db.iteritems(): #{
		path = key
		R = quotePattern.search(path)
		if R: path = R.group(1)
		try: #{{
			obj = FileInfo(path, calcsums=False)
		#}
		except: #{
			delete_list[key] = True
			continue
		#}}
	#}
	if options.remove and delete_list: deletedbs(db, delete_list)
	if not options.extract: sys.exit(0)
#}
if options.extract: #{
	def write_ascii(name): #{
		fileout = os.path.splitext(files.__dict__[name])[0]
		fh = open(fileout, 'w')
		db = dbs.__dict__[name]
		item = db.first()
		while(item): #{
			key, val = item
			fh.write('%s\t%s\n' % (key, val))
			try: item = db.next()
			except: break
		#}
		fh.close()
	#}
	for name in ('symlinks', 'rhosts', 'setuids'): #{
		write_ascii(name)
	#}
#}
if options.extract or options.remove or options.table: sys.exit(0)

exclude = []
excluded = {}
for pattern in exclusions: #{
	if not pattern in excluded: #{
		excluded[pattern] =  True
		exclude.append(pattern)
	#}
#}
exclusions = exclude
excludePattern = re.compile('|'.join(exclusions))
if verbose: print 'exclude: ', exclude

if not args: #{
	for dir, d in allMounted.items(): #{
		if not (
			d.pseudo
			or d.noexec
			or d.nosuid
			or excludePattern.search(dir)
		): #{
			args.append(dir)
		#}
	#}
	args.sort()
#}
if verbose: print "ARGS: ", args

# these files should be owned by the owner of the directory and have
# permissions so that others can't read them because they may well
# have password and other critical information in them.
critical_dot_files = (
	r'\.cshrc',
	r'\.login',
	r'\.majordomo',
	r'\.ncftprc',
	r'\.netrc',
	r'\.rhosts',
	r'\.shosts',	# ssh file
	r'\.rsync-filter',	# rsync backup filters
);
critical_dot_pattern = re.compile('/' + '$|/'.join(critical_dot_files) + '$')
if verbose: print critical_dot_pattern

ignorePattern = getExclusions(files.ignore)
ignore_file = None
if ignorePattern: #{
	pattern = '|'.join(ignorePattern)
	if verbose: print pattern
	ignorePattern = re.compile(pattern)
	ignore_file = open((files.ignore + '_files'), 'w')
#}
if verbose: print 'ignorePattern: ', ignorePattern

links_changes = 0
backup_special = ()

os.chdir('/')

symlinks	= dbs.symlinks
rhosts		= dbs.rhosts
setuids		= dbs.setuids
realpath	= options.realpath
linksChanged	= 0

skipDirs = (
	'/.aw',
	'/.autofsck',
	'/.automount',
	'/.autorelabel',
)
if verbose: print 'skipDirs: %s' % '\n'.join(skipDirs )

def scanDirectory(dir, xdev=None, baselen=0): #{
	global linksChanged

	if not dir in skipDirs: #{
		for p in Csys.find(dir, xdev=xdev, skipDirs=skipDirs): #{
			path = p.fname
			if ignorePattern and ignorePattern.search(path): #{
				ignore_file.write('!%s\n' % path)
			#}
			exclude = excludePattern.search(path)
			if p.islink: #{{
				if not exclude: #{
					if verbose: print 'symlink >%s<' % path
					key = '!' + path
					try:	oldrec = symlinks[key]
					except:	oldrec = None
					if not oldrec or realpath: #{
						ll_out = os.readlink(path)
						symlinks[key] = ll_out
						linksChanged += 1
					#}
				#}
			#}
			elif p.isfile and (p.suid or p.sgid): #{
				if verbose: print 'setuid >%s<' % path
				try: setuid = setuids[path] #{
				except: #{
					print 'new setuid %s' % path
					setuids[path] = 'R'
				#}}
			#}
			elif p.isfile and critical_dot_pattern.search(path): #{
				if verbose: print 'rhosts >%s<' % path
				try: rhost = rhosts[path] #{
				except: #{
					print 'new rhosts %s' % path
					rhosts[path] = 'R'
				#}}
			#}}
		#}
	#}
#} scanDirectory

for filesys in args: #{
	if not allMounted[filesys].ro: #{
		csbackup = os.path.join(filesys, 'csbackup')
		nonfiles = os.path.join(csbackup, 'nonfiles')
		if verbose: print 'here', filesys, csbackup, nonfiles
		Csys.mkpath(csbackup, mode=0700)
	#}
	scanDirectory(filesys, xdev=True)
#}
