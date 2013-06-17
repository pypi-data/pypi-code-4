#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/cssecscan.py,v 1.3 2013/06/11 19:53:38 csoftmgr Exp $
# $Date: 2013/06/11 19:53:38 $

import Csys, os, os.path, sys, re, stat
import time

__doc__ = '''Celestial Software Security Scan

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: cssecscan.py,v 1.3 2013/06/11 19:53:38 csoftmgr Exp $
'''

__version__='$Revision: 1.3 $'[11:-2]

configDir = os.path.join(Csys.prefix, 'var/tripwire')

configFiles = Csys.CSClassBase({
	'dbconfig'	: os.path.join(configDir, 'configure.db'),
	'tw_config'	: os.path.join(configDir, 'tw.config'),
	'dbmnew'	: os.path.join(configDir, 'filedb.db'),
	'dbmold'	: os.path.join(configDir, 'fileinfo.db'),
	'shelve'	: os.path.join(configDir, 'compare.db'),
})

import bsddb, anydbm
import cPickle
from Csys.Edits import i2s

from whichdb import whichdb

timefmt = '%a %b %e %T %Z %Y'

def dbm2bsdbbtree(fname, keysub=None, valsub=None): #{
	'''Convert hash file to Berkeley btree

	keysub and valsub may be functions to modify the
	key and values respectively.
	'''
	hash	= anydbm.open(fname, 'r')
	fout	= os.path.splitext(fname)[0] + '.db'
	st		= os.stat(fname)
	dbout	= bsddb.btopen(fout, 'n', st.st_mode)
	os.chown(fout, st.st_uid, st.st_gid)
	key		= hash.firstkey()
	while(key): #{
		if keysub:	nkey = keysub(key)
		else:		nkey = key

		if valsub:	val = valsub(hash[key])
		else:		val = hash[key]

		dbout[nkey] = val
		key = hash.nextkey(key)
	#}
	hash.close()
	return dbout
#} dbm2bsdbbtree

# Routines to cache user and group names
_gidmap = {}
from grp import getgrgid

def gidname(gid): #{
	'''Return Group Name given gid'''
	try: return _gidmap[gid]
	except: pass
	try: gname = getgrgid(gid)[0]
	except: gname = gid
	_gidmap[gid] = gname
	return(gname)
#} gidname

_uidmap = {}
from pwd import getpwuid

def uidname(uid): #{
	'''Return Group Name given uid'''
	try: return _uidmap[uid]
	except: pass
	try: uname = getpwuid(uid)[0]
	except: uname = uid
	_uidmap[uid] = uname
	return(uname)
#} gidname

commentPattern = re.compile(r'\s*#.*')
includePattern	= re.compile(r'^@@include\s+"(.*)"')
quotedPattern = re.compile(r'^(.*)"(.*)"')
configPattern = re.compile(r'^(.*)\s+(\S+)$')

def getDbFile(fname, dbconfig): #{
	'''Get entries from a hash or btreefile'''
	base, ext = os.path.splitext(fname)
	dbfile = base + '.db'
	# use the bsddb file if it exists
	if ext == '.gdbm' and os.path.exists(base + '.db'): #{
		ext = '.db'
		fname = base + ext
	#}
	if ext == '.gdbm': #{{
		dbm = anydbm.open(fname, 'r')
		key = dbm.firstkey()
		while(key): #{
			# removes double quotes around keys
			k = quotedPattern.sub(r'\1\2', key)
			dbconfig[k] = dbm[key]
			key = dbm.nextkey(key)
		#}
		dbm.close()
	#}
	else: #{
		dbm = bsddb.btopen(fname)
		for key, val in dbm.iteritems(): #{
			k = quotedPattern.sub(r'\1\2', key)
			dbconfig[k] = val
		#}
		dbm.close()
	#}}
#} getDbFile

def getConfig(fname, dbconfig): #{
	fh = open(fname)
	for line in fh: #{
		line = commentPattern.sub('', line.strip())
		if line: #{
			R = includePattern.match(line)
			if R: #{{
				fname = R.group(1)
				for ext in ('.db', '.gdbm'): #{{
					dbfile = fname + ext
					if os.path.isfile(dbfile): #{
						getDbFile(dbfile, dbconfig)
						break
					#}
				else: #{
					# this is only executed if the break above
					# wasn't hit.
					getConfig(fname, dbconfig)
				#}}
			#}
			else: #{
				R = configPattern.match(line)
				if R: #{{
					parts = R.groups()
				#}
				else: #{
					parts = [line, None]
				#}}
				dbconfig[parts[0]] = parts[1]
			#}}
		#}
	#}
#}
csvDelim = None

# for backwards compatibility
MyStat = FileInfo = Csys.FileInfo

# start main program
if __name__ == '__main__': #{
	if os.geteuid() != 0: #{
		sys.stderr.write('Only root can run %s\n' % Csys.Config.progname)
		# s = FileInfo('/usr/share/misc/termcap', calcsums=True)
		# print s.prettyprint()
		sys.exit(0)
	#}
	# check for old shelve file
	if os.path.isfile(configFiles.shelve): #{
		import shelve
		sys.stderr.write('%s: converting shelve hash to btree' % Csys.Config.progname)
		fh_in	= shelve.open(configFiles.shelve, 'r')
		btree	= bsddb.btopen(configFiles.dbmold, 'n', 0600)
		for key in fh_in.keys(): btree[key] = cPickle.dumps(fh_in[key])
		fh_in.close()
		btree.close()
		os.unlink(configFiles.shelve)
	#}
	# Add program options to parser here

	def setOptions(): #{
		'''Set command line options'''
		global __doc__

		parser = Csys.getopts(__doc__)

		parser.add_option('-q', '--query',
			action='append', type='string', dest='query', default=[],
			help='Query Entry from fileinfo',
		)
		parser.add_option('-r', '--reportonly',
			action='store_true', dest='reportonly', default=False,
			help='Skip processing, report only',
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

	header = (
		'%s,v %s Security Scan'
		' New, Changed, and Missing files\n'
	) % (Csys.Config.progname, __version__)

	def printit(msg): #{
		global header
		if header: print header
		header = ''
		print msg
	#} printit

	if options.query: #{{
		dbmold = bsddb.btopen(configFiles.dbmold, 'r')
		for key in options.query: #{
			val = dbmold[key]
			print val
			newrec = FileInfo(key, True)
			oldrec = FileInfo.to_python(key, dbmold[key])
			print 'old: %s\nnew: %s' % (
				oldrec.prettyprint(),
				newrec.prettyprint(),
			)
		#}
		sys.exit(0)
	#}
	if not options.reportonly: #{{
		dbconfig = bsddb.btopen(configFiles.dbconfig, 'n', 0600)

		tw_config = configFiles.tw_config

		getConfig(tw_config, dbconfig)

		dbmnew = bsddb.btopen(configFiles.dbmnew, 'n', 0600)

		if not os.path.isfile(configFiles.dbmold): dbmold = None
		else: dbmold = bsddb.btopen(configFiles.dbmold, 'r')

		dirs = []
		item = dbconfig.set_location('/')
		while(item): #{
			key, val = item
			if not key[0] == '/': break
			try: rec = FileInfo(key, True, type=val)
			except: rec = None
			if rec: #{
				try: #{{
					oldrec = FileInfo.to_python(key, dbmold[key])
					rec.changed = int(oldrec != rec)
				#}
				except: #{
					pass
				#}}
				dbmnew[key] = str(rec)
				if verbose: print('%s >%s<' % (key, val))
				if rec.isdir: dirs.append(key)
			#}
			try: item = dbconfig.next()
			except: break
		#}
		item = dbconfig.set_location('=')
		while(item): #{
			key, val = item
			if not key[0] == '=': break
			key = key[1:] # strip leading character
			try: rec = FileInfo(key, True, type=val)
			except: rec = None
			if rec: #{
				dbmnew[key] = str(rec)
				if verbose: print('%s >%s<' % (key, val))
				# if rec.isdir: dirs.append(key)
			#}
			try: item = dbconfig.next()
			except: break
		#}
		def scanDirectory(dir): #{
			if verbose: print('scanDirectory(%s)' % dir)
			if ('=' + dir) in dbconfig: return
			dirRec	= FileInfo.to_python(dir, dbmnew[dir])
			dirType	= dirRec.type
			entries	= os.listdir(dir)
			entries.sort()
			for entry in entries: #{
				p = os.path.join(dir, entry)
				if ('!' + p) in dbconfig: continue
				if verbose: print('\t%s' % p)
				try: rec = FileInfo.to_python(p, dbmnew[p]) #{
				except: #{
					try: oldrec = FileInfo.to_python(p, dbmold[p])
					except: oldrec = None

					try: rec = FileInfo(p, not oldrec, type=dirType)
					except: continue
					if (oldrec): #{
						rec.changed = cmp(
							(oldrec.st_mode, oldrec.st_ctime, oldrec.st_size),
							(rec.st_mode, rec.st_ctime, rec.st_size)
						)
						if rec.changed: rec.calcsums()
						else: #{
							rec.md5 = oldrec.md5
							rec.sha = oldrec.sha
						#}
					#}

					dbmnew[p] = str(rec)
				#}}
				if rec.isdir: scanDirectory(p)
			#}
		#} scanDirectory

		if verbose: print 'start scanDirectoy'
		for dir in dirs: scanDirectory(dir)

		# if verbose: print 'writing filedb.db'
		# for rec in recs.values(): dbmnew[rec.fname] = str(rec)
	#}
	else: #{
		if not os.path.isfile(configFiles.dbmold): dbmold = None
		else: dbmold = bsddb.btopen(configFiles.dbmold, 'r')
		if not os.path.isfile(configFiles.dbmnew): dbmnew = None
		else: dbmnew = bsddb.btopen(configFiles.dbmnew, 'r')
	#}}

	if not dbmold: #{{
		dbmnew.close()
		if verbose: print 'creating %s' % configFiles.dbmold
		os.rename(configFiles.dbmnew, configFiles.dbmold)
	#}
	else: #{
		if verbose: print 'getting oldrecs'

		oldrecs = {}.fromkeys(dbmold.keys(), True)
		if verbose: print 'start comparisons'
		count = changes = adds = missing = 0
		for key, val in dbmnew.iteritems(): #{
			count += 1
			rec = FileInfo.to_python(key, val)
			try: #{{
				# keep track of missing items
				del oldrecs[key]
				if rec.changed: #{
					oldrec = FileInfo.to_python(key, dbmold[key])
					rec.changed = rec != oldrec
					if rec.changed: #{
						changes += 1
						printit('old: %s' % oldrec.prettyprint())
						printit('new: %s\n' % rec.prettyprint())
					#}
				#}
			#}
			except KeyError: #{
				adds += 1
				printit('add: %s\n' % rec.prettyprint())
			#}}
		#}
		keys = oldrecs.keys()
		keys.sort()
		for key in keys: #{
			missing += 1
			try: #{{
				rec = FileInfo.to_python(key, dbmold[key])
				printit('missing: %s\n' % rec.prettyprint())
			#}
			except KeyError: #{
				printit('missing: %s\n\tKeyError\n' % key)
			#}}
		#}
		if not header: #{
			print 'Proccessed %s Changes %s Adds %s Missing %s' % (
				i2s(count),
				i2s(changes),
				i2s(adds),
				i2s(missing),
			)
		#}
		dbmold.close()
		dbmnew.close()
	#}}
#}
