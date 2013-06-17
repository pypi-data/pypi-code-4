# Celestial Software Utilities
import os, sys, re, stat

__version__ = "0.1"

__doc__ = '''Celestial Software Utilities'''

# Python 2.6 (and possibly earlier).
try: #{{
	from hashlib import md5
	from hashlib import sha1 as sha
#}
except ImportError: #{
	from md5 import new as md5
	from sha import new as sha
#}}
from Csys.Edits import detab

prefix	= sys.prefix

l_prefix = prefix

prefixes = [os.path.join(prefix, 'local'), prefix]
try: #{{
	for pfix in [s.strip() for s in open('/etc/openpkg').readlines()]: #{
		if pfix: #{
			prefixes.extend([os.path.join(pfix, 'local'), pfix])
		#}
	#}
#}
except IOError: #{
	pass
#}}
prefixes.extend(['/usr/local', '/'])

def list2dict(l): #{
	'''Convert list to dictionary'''
	assert (len(l) % 2 == 0), 'list2dict: length %d not modulo 2' % len(l)
	d = dict(zip(l[0::2], l[1::2]))
	return d
#} list2dict

class Error(Exception): #{
	'''Base class for Csys.Sysutils exceptions'''
	def __init__(self, msg=''): #{
		self.message = msg
		Exception.__init__(self, msg)
	#}

	def __str__(self): return(self.message)

	def __repr__(self): return('Error(%s)' % repr(self.message))

#} class Error

class KWArgs(object): #{
	'''Short cut for key word arguments
	
	This will normally be using with commands like the following:
		def sumfunc(self, arg1, arg2, **kwargs): #{
			kw = Csys.KWArgs(defaultargs, kwargs)
			kw1 = kw.kw1
			...
		#}
		sumfunc(arg1, arg2, kw1=val, kw2=val2)
	'''
	def __init__(self, defaultargs, raiseError=True, **kwargs): #{
		cols = self.__dict__
		if raiseError: #{ check for invalid key word argument
			for key in kwargs.keys(): #{
				if not key in defaultargs:
					raise Error('KWArgs: invalid key word >%s<' % key)
			#}
		#}
		for k, v in defaultargs.items(): #{
			try: cols[k] = kwargs[k]
			except KeyError: cols[k] = v
		#}
	#}
#} class KWArgs

# utility definitions for types
typeARRAY	= type([])
typeLIST	= type([])
typeTUPLE	= type(())
typeDICT	= type({})
typeSTR		= type('')
import copy

XML_translations = (
	('>', '&gt;'),
	('<', '&lg;'),
)
def ascii2xml(src): #{
	'''Translate ascii text to XML notation'''
	for a, x in XML_translations: src = src.replace(a, x)
	return src
#} ascii2xml

def xml2ascii(src): #{
	'''Translate ascii text to XML notation'''
	for a, x in XML_translations: src = src.replace(x, a)
	return src
#} xml2ascii

class CSClassBase(object): #{
	'''Simple class which may provide a shortcut for dictionaries'''

	def __init__(self, kwargs={}): #{
		self.__dict__.update(kwargs)
	#} __init__

	def dumpAttrs(self): #{
		'''Debug dump of attributes'''
		cols = self.__dict__
		keys = cols.keys()
		keys.sort()
		print 'dumpAttrs'
		for key in keys: #{
			try: print key, cols[key]
			except: print '\tcannot print %s' % key
		#}
	#} dumpAttrs

#} class CSClassBase

class CSClassDict(CSClassBase): #{
	'''Class to wrap external dictionary'''
	def __init__(self, kwargs={}): self.__dict__ = kwargs

#} class CSClassDict

class CSClass(CSClassBase): #{
	'''Base class with attributes and keywork parsing'''
	__doc__ = ('''
	This class is used as the generic base class for classes with attributes
	in a dictionary, _attributes, which may be modified by key word arguments.

	The idiom for using this is:

	class SomeClass(Csys.CSClass [, ...]):
		_attributes = {
			... definitions
		}
		def __init__(self, arg1, ..., **kwargs):
			Csys.CSClass.__init__(self, *kwargs)
			...
	''')
	_attributes = {}
	def __init__(self, raiseError=True, **kwargs): #{
		if not hasattr(self, '_kwargs'): #{
			cols = self.__dict__
			# Copy default attributes
			for k, v in self._attributes.items(): #{
				T = type(v)
				# copy array and dictionary types
				if   T == typeARRAY: cols[k] = v[:]
				elif T == typeDICT: cols[k] = copy.deepcopy(v)
				else: cols[k] = v
			#}
			for k, v in kwargs.items(): #{
				if not k.startswith('_'): #{ don't muck with private attributes
					if k in cols: cols[k] = v
					elif raiseError: raise Error('%s: invalid key word >%s<' % (self.__class__, k))
				#}
			#}
			cols['_kwargs'] = kwargs # aave for possible later use
		#}
	#} __init__

	def getSQLObject(self, classname=None, keys=None, wantarray=False): #{
		'''Skeleton class definition for SQLObject'''
		if classname is None: #{
			classname = self.__class__[0].upper() + self.__class__[1:].lower()
		#}
		cols = self.__dict__
		if keys is None: #{
			keys = cols.keys()
			keys.sort()
		#}
		output = [
			'class %s(SQLObject): #{' % classname,
		]
		# compute maximum length of fields
		n = 0
		for key in keys: n = max(n, len(key))
		fmt = '\t%%-%ds = StringCol()' % n
		
		for key in keys: output.append(fmt % key)
		
		output.append('#} class %s' % classname)
		if wantarray: return output
		return '\n'.join(output)
	#} getSQLObject

	def getSQLObjectData(self, keys=None): #{
		'''Return dictionary to load SQLObject'''
		cols = self.__dict__
		keymap = cols.get('_SQLObjectKeyMap', {})
		if keys is None: #{
			keys = []
			for key in cols.keys(): #{
				if key[0] != '_': keys.append(key)
			#}
		#}
		result = {}
		for key in keys: #{
			mapkey = keymap.get(key, key)
			if mapkey: result[mapkey] = cols[key]
		#}
		try: result['st_mtime'] = self.cfg._st_mtime
		except: pass

		return result
	#} getSQLObjectData

	def dump2xml(self, root=None, attrsonly=False, wantarray=False): #{
		'''Simple XML encapsulation'''
		if root is None: root = str(self.__class__).replace('.', '_')
		output = ['<%s>' % root ]
		cols = self.__dict__
		keys = cols.keys()
		keys.sort()
		for key in keys: #{
			if (key[0] == '_'
				or attrsonly and not key in self._attributes
			): continue
			tag		= ('\t<%s>' % key)
			tagend	= ('\t</%s>' % key)
			try: val = cols[key]
			except: continue
			tval = type(val)
			if tval in (typeLIST, typeTUPLE): #{
				output.append(tag)
				for d in tval: #{
					output.append('\t\t<data>%s</data>' % ascii2xml(str(d)))
				#}
				output.append(tagend)
			#}
			elif tval == typeDICT: #{
				tkeys = tval.keys()
				tkeys.sort()
				output.append(tag)
				for tkey in tkeys: #{
					d = tkeys[tkey]
					output.append(
						'\t\t<data id="%s">%s</data>' % (tkey, ascii2xml(str(d)))
					)
				#}
				output.append(tagend)
			#}
			else: #{
				output.append('%s%s%s' % (tag, ascii2xml(str(val)), tagend[1:]))
			#}
		#}
		output.append('</%s>' % root)
		if wantarray: return output
		return '\n'.join(output)
	#} dump2xml

#} CSClass

__doc__ += ('''
	Slice operations which implement funcationallity similar to the perl
	hash slices mapping lists of key names with values.

	getSlice(fields, dict) -> list of values in order of fields

	setSlice(fields, vals) -> dictionary with fields as keys

	updSlice(dst, fields, vals) -> updates dst dictionary
''')

def getSlice(fields, dict): #{
	'''Return a list of values from dict'''
	return([dict[x] for x in fields])
#} getSlice

def setSlice(fields, vals): #{
	'''Return dictionary with fields mapped to vals'''
	return(dict(zip(fields, vals)))
#} setSlice

def updSlice(dst, fields, vals): #{
	'''Update fields in dst with vals'''
	dst.update(dict(zip(fields, vals)))
	return dst
#} updSlice

def delSlice(fields, dict): #{
	'''Remove fields from dict

	Fields may be a list or tuple of field names, or a dictionary
	'''
	if hasattr(fields, 'keys'): fields = fields.keys()
	for key in fields: #{
		try: dict.pop(key)
		except KeyError: pass
	#}
#} delSlice

class _Config(CSClass): #{
	'''General configuration parameters'''
	_attributes = {
		'prefix'	: l_prefix,
		'l_prefix'	: l_prefix,
		# 'sendmail'	: os.path.join(l_prefix, 'sbin', 'sendmail'),
	}
	_fieldMaps = {
		'hostname'	: ('hostname', 'hostname_short', 'host_ip', 'domain'),
		'uname'		: ('ostype', 'nodename', 'os_release', 'os_version', 'machine'),
		'progname'	: ('dirname', 'progname'),
		'rpm'		: ('rpm', 'bash'),
	}
	def __init__(self): #{
		CSClass.__init__(self)
	#} __init__

	def __getattr__(self, attr): #{
		'''Efficient method for returning on-time settings'''
		try: return(self.__dict__[attr])
		except: pass
		cols = self.__dict__
		_fieldMaps = self._fieldMaps
		if attr == 'sendmail': #{{
			for dir in prefixes: #{
				sendmail = os.path.join(dir, 'sbin', 'sendmail')
				if os.access(sendmail, os.X_OK): break
			#}
			else: #{
				sendmail = None
			#}
			cols['sendmail'] = sendmail
		#}
		elif attr in _fieldMaps['hostname']: #{
			try: #{{
				import socket
				hostname = socket.getfqdn(socket.gethostname())
				host_ip = socket.gethostbyname(hostname)
				hostname_short, domain = hostname.split('.', 1)
			#}
			except: #{
				host_ip = '127.0.0.1' # this should always work
				hostname_short = hostname = self.nodename # will automatically call uname
				domain = ''
			#}}
			updSlice(cols, _fieldMaps['hostname'],
				(hostname, hostname_short, host_ip, domain)
			)
		#}
		elif attr in _fieldMaps['uname']: #{
			updSlice(cols, _fieldMaps['uname'], os.uname())
			cols['ostype']		= cols['ostype'].lower()
			cols['nodename']	= cols['nodename'].lower()
			cols['os_release']	= cols['os_release'].lower()
		#}
		elif attr in _fieldMaps['progname']: #{
			# try/except for plpython in postgresql
			try: cols['dirname'], cols['progname'] = os.path.split(sys.argv[0])
			except: cols['dirname'] = cols['progname'] = 'unknown'
		#}
		elif attr in _fieldMaps['rpm']: #{
			# These are old defaults, and should be replaced below
			# cols['rpm'] = '/bin/rpm'
			# cols['bash'] = '/bin/bash'
			for prog in ('rpm', 'bash'): #{
				for pfix in prefixes: #{
					for lib in ('lib', 'libexec'): #{
						f = os.path.join(pfix, lib, 'openpkg', prog)
						if os.path.exists(f): #{
							cols[prog] = f
							break
						#}
					#}
				#}
				if not prog in cols: #{
					for pfix in prefixes: #{
						f = os.path.join(pfix, 'bin', prog)
						if os.path.exists(f): #{
							cols[prog] = f
							break
						#}
					#}
				#}
			#}
		#}
		elif attr == 'byteorder': #{
			cols[attr] = sys.byteorder
		#}}
		return cols[attr]
	#} __getattr__
#} class _Config

Config = _Config()

import Csys.Passwd

from optparse import OptionParser

__doc__ += ('''
	getopts(usage) returns a OptionParser parser object with
	reasonable defaults for verbose, -e for environment, and usage
	set to the usage paramter.
''')

def getopts(usage): #{
	'''Return OptionParser parser object with usage set'''

	usage = detab(usage)

	parser = OptionParser(usage=usage)

	parser.add_option('-v', '--verbose',
		action="store_true", dest="verbose", default=False,
		help="verbose output to stderr"
	)
	parser.add_option('-e', '--environ',
		action="append", type="string", dest="environ",
		help="ENVIRON ::= VAR=VALUE"
	)
	return parser
#} getopts

# The following are replacements for os.popen and os.system using
# the subprocess routines.

from subprocess import call, PIPE, Popen

def system(cmd): #{
	return call(cmd, shell=True, executable=Config.bash)
#} system

def popen(cmd, mode='r', bufsize=-1): #{
	if mode.lower()[0] == 'r': #{{
		fh = Popen(cmd, shell=True, executable=Config.bash, bufsize=bufsize, stdout=PIPE).stdout
	#}
	elif mode.lower()[0] == 'w': #{
		fh = Popen(cmd, shell=True, executable=Config.bash, bufsize=bufsize, stdin=PIPE).stdin
	#}}
	return fh
#} popen

__doc__ += ('''
	run(cmd, verbose=False, runCmd=True) -- run system command with verbose tracing.
	Setting exec False suppresses execution, showing the command
	that would be executed
''')

def run (cmd, verbose=False, runCmd=True): #{
	'''Run system command with verbose tracing'''
	if verbose : sys.stderr.writelines('run(%s)\n' % cmd)
	if runCmd: return(system(cmd))
	return 0
#}
__doc__ += ('''
	getoptionsEnvironment(options) -- sets environment variables
	from command line ``-eVAR=VALUE'' options.
''')

def getoptionsEnvironment(options): #{
	'''Set environment variables from -eVAR=VALUE arguments'''
	if options.environ: #{
		regexp = re.compile(r"(?P<var>\S+)=(?P<val>.*)")
		for environ in options.environ : #{
			result = regexp.search(environ)
			if result: #{
				var = result.group('var')
				os.environ[var] = result.group('val')
			#}
		#}
	#}
#} getoptionsEnvironment

def mkpath(path, mode=0755, uid=None, gid=None, model=None): #{
	'''Recursively mkdir

	mkpath calls os.mkdir(path, mode), recursively if necessary, to make
	the directory and all necessary parent directories.  It checks for
	exceptions, passing through any other than missing path elements.

	If the uid *AND* gid arguments are defined, it will change ownership
	as well.
	'''
	assert path, 'mkdir: path must be specified'

	if os.path.isdir(path): return

	if model: #{
		fstat	= os.stat(model)
		mode	= fstat.st_mode
		uid		= fstat.st_uid
		gid		= fstat.st_gid
	#}
	while True: #{
		try: os.mkdir(path, mode) #{
		except OSError, e: #{
			if e.errno == 17: break
			if e.errno != 2: raise
			# print 'mkpath(%s)' % path
			mkpath(os.path.dirname(path), mode, uid, gid)
			continue
		#}}
		break
	#}
	if os.geteuid() == 0 and not (uid is None and gid is None): #{
		os.chown(path, uid, gid)
	#}
	os.chmod(path, mode) # the chown may have reset the mode
#} mkpath

def expanduser(path, user=None): #{
	'''Expand ~[username]/path to full path name using pw from Csys.Passwd'''
	if user is None: user = os.environ['USER']
	# print 'expanduser(%s, %s)' % (path, user)
	if path.startswith('~'): #{
		newuser, path = path[1:].split('/', 1)
		# print 'expanduser: newuser >%s< path >%s<' % (newuser, path)
		if newuser: user = newuser
		if not isinstance(user, Csys.Passwd.Passwd): #{
			user = Csys.Passwd.getpwnam(user)
		#}
		path = '%s/%s' % (user.home, path)
	#}
	# print 'expanduser: return >%s<' % path
	return path
#} expanduser

def openOut(fname, model=None, user=None, mode=None, uid=None, gid=None, opentype='wb'): #{
	'''Open file setting attributes

	If the model argument is given, the owner, group, and mode
	will be set the same as that file.

	If the user argument is specified, the uid and gid will be
	taken from the user's information.

	If the uid *AND* gid arguments are specified they will be
	used in chown to set the ownership.
	'''
	fh = open(fname, opentype)
	if os.getuid() != 0: user = uid = gid = None
	if model: #{
		fstat = os.stat(model)
		uid, gid, mode = fstat.st_uid, fstat.st_gid, fstat.st_mode
	#}
	elif user: #{
		if not isinstance(user, Csys.Passwd.Passwd): #{
			user = Csys.Passwd.getpwnam(user)
		#}
		uid, gid = user.uid, user.gid
	#}
	# print 'expanduser: ', user, uid, gid
	if not uid is None: os.chown(fname, uid, gid)
	if not mode is None: os.chmod(fname, mode)
	return fh
#} openOut

def replacefile(dst, src, user=None, mode=None, uid=None, gid=None, model=None, utime=None, srctype='rb', dsttype='wb'): #{
	'''Replace dst file leaving old copy in dst.bak'''
	if os.path.isfile(dst): #{{
		model = dst
		oldname = dst + '.bak'
		newname = dst + '.new'
	#}
	else: #{
		oldname = None
		newname = dst
	#}}
	fhout = openOut(
		newname, model=model, user=user, mode=mode, uid=uid, gid=gid,
		opentype=dsttype
	)
	# convert array to string if necessary
	if type(src) == typeLIST: src = '\n'.join(src) + '\n'
	fhout.write(src)
	fhout.close()
	if oldname: #{
		os.rename(dst, oldname)
		os.rename(newname, dst)
	#}
# replacefile

def copyfile(src, dst, user=None, mode=None, uid=None, gid=None, model=None, utime=None, srctype='rb', dsttype='wb'): #{
	'''Copy src file to dst setting ownership and permissions
	
	If the model argument is given, the owner, group, and mode
	will be set the same as that file.

	If the user argument is specified, the uid and gid will be
	taken from the user's information.

	If the uid *AND* gid arguments are specified they will be
	used in chown to set the ownership.

	If utime is not None, the dst access and modification times
	will be set to the same as the source file.
	'''
	fhinput = open(src, srctype)
	fhoutput = openOut(dst, model, user, mode, uid, gid, dsttype)
	for line in fhinput: fhoutput.write(line)
	fhinput.close()
	fhoutput.close()
	if not utime is None: #{
		fstat = os.stat(src)
		os.utime(dst, (fstat.st_atime, fstat.st_mtime))
	#}
#} copyfile

# These patterns are for removing comments from input including C
# style /* ... */, C++, and the rather normal '#'.

_CPattern			= re.compile( r'/\*.*?\*/', re.DOTALL )
_CplusplusPattern	= re.compile( r'//.*$',	re.MULTILINE)
_HashPattern		= re.compile( r'#.*$',	re.MULTILINE)
_RstripPattern		= re.compile( r'^\s+$',	re.MULTILINE)
_SQLPattern			= re.compile( r'^\s*--\s.*$',	re.MULTILINE)
_HTMLPattern		= re.compile( r'<!--.*?-->', re.DOTALL )

_multiBlankLines = re.compile(r'\n{3,}', re.DOTALL)

def rmComments(input,
	hash=True, C=False, Cplusplus=False, all=False,
	SQL=False,
	HTML=False,
	wantarray=False,
	pattern=None
): #{
	'''Remove comments and trailing whitespace from input line
	
	The input my be a string, list, tuple, or object with
	readlines().  NOTE: if a file type object is used, it will
	*NOT* be closed to allow things like StringIO objects to be
	used after calling rmComments.

	The arguments, hash, C, Cplusplus, and all determine which
	comments will be removed from the input.  The default
	arguments will only remove comments starting with ``#''
	characters.  Setting all=True turns all options on which is
	useful for things like php code which supports all three
	types of comments.

	Setting wantarray=True returns an array of lines split on the
	'\n' character, otherwise a string is returned.

	If pattern is set, then only lines matching the pattern will be
	returned.  This requires converting the resulting line to an
	array, and may require converting back to a string depending
	on the setting of wantarray.  The value assigned to pattern may
	be a compiled regular expression or a string containing the
	regular expression.
	'''
	if hasattr(input, 'readlines') or hasattr(input, 'readline'): #{{
		input = [line for line in input]
	#}
	if type(input) in (typeARRAY, typeTUPLE): line = ''.join(input)
	else: line = input
	patterns = []
	if all: hash = C = Cplusplus = SQL = True
	if C:			patterns.append(_CPattern)
	if Cplusplus:	patterns.append(_CplusplusPattern)
	if SQL or hash:	patterns.append(_HashPattern)
	if SQL:			patterns.append(_SQLPattern)
	if HTML:		patterns.append(_HTMLPattern)
	patterns.append(_RstripPattern)
	for pat in patterns: #{
		# print 'pattern: ', pattern
		oldline = '';
		while line != oldline: #{
			oldline = line
			line, n = pat.subn('', line)
		#}
		if not line: break
	#}
	if pattern or wantarray: #{
		output = line.split('\n')
		if pattern: output = grep(pattern, output)
		if wantarray: return output
		line = '\n'.join(output)
	#}
	line = line.rstrip()
	return(line)
#} rmComments

_continuation = re.compile(r'^\s')

def mklines(src): #{
	'''E-Mail Alias join lines'''
	lines = rmComments(src, wantarray=True)
	output = []
	outlines = []
	for line in lines: #{
		if not line: continue
		if _continuation.match(line): #{
			outlines.append(line.strip())
			continue
		#}
		if outlines: output.append(' '.join(outlines))
		outlines = [line]
	#}
	if outlines: output.append(' '.join(outlines))
	return output
#} mklines

import ConfigParser as SysConfigParser

COMMA_SPACES	= re.compile(r'[,\s]+')
COMMA_SPACES_NL	= re.compile(r'[,\s\n]+', re.DOTALL)

class ConfigParser(SysConfigParser.ConfigParser): #{
	'''ConfigParser.ConfigParser extensions adding rewrite'''

	def __init__(self, filenames=None, writename=None): #{
		SysConfigParser.ConfigParser.__init__(self)
		if filenames: self.readfiles(filenames, writename)
	#} __init__

	def readfiles(self, filenames, writename=None): #{
		'''Save last file name for rewrite later'''
		if writename: self._writename = writename #{
		else: #{
			if isinstance(filenames, basestring): filenames = [filenames]
			# This will get the *LAST* file
			self._writename = filenames[-1:][0]
		#}}
		self.read(filenames)
		try: #{{
			s = os.stat(self._writename)
			self._st_mtime = s.st_mtime
		#}
		except: #{
			self._st_mtime = 0
		#}}
	#} readfiles

	def rewrite(self, fname=None, user=None, mode=0644): #{
		'''(re)write fname or last argument of readFiles'''
		if hasattr(fname, 'write'): #{{
			fh = fname
			newfname = None
		#}
		else: #{
			if fname is None: fname = self._writename
			newfname = fname + '.new'
			bakfname = fname + '.bak'
			if os.access(fname, os.X_OK): model=fname
			else: model=None
			fh = openOut(newfname, model=model, mode=mode)
		#}}
		self.write(fh)
		fh.close()
		if newfname: #{
			if model: os.rename(fname, bakfname)
			os.rename(newfname, fname)
		#}
	#} rewrite

	def getDict(self, section, defaults=None, asClass=False, raw=False, vars=None): #{
		'''Return dictionary of section'''
		try: cols = dict(self.items(section, raw, vars)) #{
		except: #{
			if defaults is None: cols = self.defaults()
			else: cols = defaults
		#}}
		if asClass: return(CSClassBase(cols))
		return cols
	#} getDict

	def getClass(self, section, defaults=None, raw=False, vars=None, **kwargs): #{
		'''Return section as class

		This is similar to getDict(...asClass=True) except that it
		uses the ConfigParser getxxx functions instead of taking
		things from the dictionary directly.

		asBoolean == list of fields to be returned with getboolean

		asInt == list of fields with getint (missing fields 0)

		asList == list of fields to be returned as list.

		asLines == list of lines (split on '\n' in lists

		asFloat == list of fields to be returned as floats
		'''

		cols = {}
		options = set(self.options(section))
		asBoolean = set(kwargs.get('asBoolean', []))
		for key in asBoolean: #{
			cols[key] = (key in options and self.getboolean(section, key)) 
		#}
		options -= asBoolean

		asInt = set(kwargs.get('asInt', []))
		for key in asInt: #{
			val = 0
			if key in options: val = self.getint(section, key)
			cols[key] = val
		#}
		options -= asInt

		asFloat = set(kwargs.get('asFloat', []))
		for key in asFloat: #{
			val = 0
			if key in options: val = self.getfloat(section, key, raw, vars)
			cols[key] = val
		#}
		options -= asFloat

		asList = set(kwargs.get('asList', []))
		for key in asList: #{
			val = []
			if key in options: #{
				val = [
					s.strip() for s in COMMA_SPACES.split(self.get(section, key, raw, vars)) if s.strip()
				]
			#}
			cols[key] = val
		#}
		options -= asList

		asLines = set(kwargs.get('asLines', []))
		for key in asLines: #{
			val = []
			if key in options: #{
				val = [
					s.strip() for s in self.get(section, key, raw, vars).split('\n') if s.strip()
				]
			#}
			cols[key] = val
		#}
		options -= asLines

		for key in options: #{
			cols[key] = self.get(section, key)
		#}
		return(CSClassBase(cols))
	#} getClass

	def getAll(self, raw=False, vars=None): #{
		'''return dictionary of all sections'''
		rc = {
			'default' : self.defaults()
		}
		for section in self.sections(): #{
			rc[section] = dict(self.items(section, raw, vars))
		#}
		return rc
	#} getAll

	def getList(self, section, option, raw=False, vars=None): #{
		'''Return option as a list'''
		try: #{{
			s = self.get(section, option, raw, vars)
			return(grep('.', COMMA_SPACES.split(s.strip())))
		#}
		except: return [] #}
	#} getList

	def getLines(self, section, option, raw=False, vars=None): #{
		'''Return option as a list'''
		try: #{{
			s = self.get(section, option, raw, vars)
			return [
				f.strip() for f in s.split('\n') if f.strip()
			]
		#}
		except: return [] #}
	#} getLines

#} class ConfigParser

def grep(pattern, input=None, file=None, quick=False): #{
	'''Return list of items in input matching pattern'''
	if not hasattr(pattern, 'search'): pattern = re.compile(pattern)
	if input is None: input = []
	output = []
	if file: #{
		try: #{{
			if hasattr(file, 'readlines'): fh = file
			else: fh = open(file)
			input = [line.rstrip() for line in fh]
			fh.close()
		#}
		except: #{
			return output
		#}}
	#}
	for line in input: #{
		if pattern.search(line): #{
			output.append(line)
			if quick: break
		#}
	#}
	return output
#} grep

def printbool(bool): #{
	'''Print True or False for boolean value for debugging'''
	if bool: return 'True'
	return 'False'
#} printbool

class CSClassConfig(CSClass): #{
	filename	= None	# configuration file name
	section		= 'DEFAULT'	# Section header in file
	user		= Csys.Passwd.getpwnam('root')
	uid			= user.uid
	gid			= user.gid
	mode		= 0644

	_attributeList = tuple()
	_attributes = {}

	def getSQLObject(self, classname=None, wantarray=False): #{
		'''Skeleton class definition for SQLObject'''
		keys = []
		_attributeList = self._attributeList
		for i in range(0, len(_attributeList), 2): #{
			key = _attributeList[i]
			if key[0] != '_': l = keys.append(key)
		#}
		return Csys.CSClass.getSQLObject(self,
			classname	= classname,
			keys		= keys,
			wantarray	= wantarray,
		)
	#} getSQLObject

	def configOutput(self): #{
		'''Generate Configuration output'''
		if not hasattr(self, '_fmt'): #{
			output = [ '[%s]' % self.section ]
			# get max key length
			l = 0
			_attributeList = self._attributeList
			for i in range(0, len(_attributeList), 2): #{
				key = _attributeList[i]
				if key[0] != '_': l = max(len(key), l)
			#}
			fmt = '%%-%ds = %%%%(%%s)s' % l
			for i in range(0, len(_attributeList), 2): #{
				key = _attributeList[i]
				if key[0] != '_': output.append(fmt % (key, key))
			#}
			output.append('')
			self._fmt = '\n'.join(output)
		#}
		return self._fmt % self.__dict__
	#} configOutput

	def rewrite(self, fname=None, user=None, mode=None): #{
		if fname is None: fname = self.filename
		if hasattr(fname, 'write'): #{{
			fh = fname
		#}
		else : #{
			if user is None: user = self.user
			if mode is None: mode = self.mode
			if os.path.isfile(fname): #{
				bakfile = fname + '.bak'
				copyfile(fname, bakfile, model=fname)
				model = bakfile
				fh = openOut(fname, model=bakfile)
			#}
			else: #{
				fh = openOut(fname,
					user=user, uid=self.uid, gid=self.gid, mode=mode
				)
			#}
		#}}
		fh.write(self.configOutput())
		fh.close()
	#} rewrite
#} class CSClassConfig

def writeTemplates(dstdir, templates, rec, pattern='CSADMIN', protected=None): #{
	'''Write files from templates

    dstdir      destination directory
    templates   directory containing templates
    rec         dictionary containing fields to complete templates
    pattern     Pattern in destination files to check for existence
	'''

	# There's nothing to do if there's no templates directory
	if not os.path.isdir(templates): return

	# import cPickle as pickle
	import cPickle as pickle
	pname			= '.cs_stats'
	protectname		= '.cs_notemplates'
	cfgname			= '.cs_installed.ini'
	cfgchanges		= False
	cfg				= ConfigParser()
	cfgfile			= os.path.join(dstdir, cfgname)
	cfg.readfiles(cfgfile)
	cfgsection		= 'installed'
	if not cfg.has_section(cfgsection): #{
		cfgchanges	= True
		cfg.add_section(cfgsection)
	#}
	skip_entries	= (
		pname,
		protectname,
		'CVS',
	)
	if protected is None: #{
		protectfile	= os.path.join(templates, protectname)
		protected	= os.path.isfile(protectfile)
	#}
	pfile			= os.path.join(templates, pname)
	try: #{
		fh = open(pfile, 'r')
		fstats = pickle.load(fh)
		fh.close()
	except: fstats = {}
	#}
	# sort the template entries for consistency
	entries = os.listdir(templates)
	entries.sort()
	for template in entries: #{
		if template in skip_entries: continue
		tempfile = os.path.join(templates, template)
		if os.path.isdir(tempfile): #{
			# set up recursive copy
			newdest = os.path.join(dstdir, template)
			mkpath(newdest, model=dstdir)
			writeTemplates( newdest,
				os.path.join(templates, template), rec, pattern, protected
			)
			continue
		#}
		fstat = fstats.get(template)
		conffile = os.path.join(dstdir, template)

		try: fileConfigured = cfg.getboolean(cfgsection, template)
		except: fileConfigured = None
		
		if fileConfigured is None: #{
			fileConfigured = grep(pattern, file=conffile)
			if fileConfigured: #{
				cfgchanges = True
				cfg.set(cfgsection, template, 'True')
			#}
		#}
		if os.path.isfile(tempfile) and not fileConfigured: #{
			cfgchanges = True
			cfg.set(cfgsection, template, 'True')
			# print 'writeTemplate: >%s<' % tempfile
			fh = open(tempfile)
			fmt = ''.join(fh.readlines())
			fh.close()

			try: outstring = fmt % rec #{
			except: #{
				fh = openOut('/tmp/dbugfmt', mode=0600)
				print 'fmt error on >%s<' % tempfile
				pickle.dump(fmt, fh)
				pickle.dump(rec, fh)
				fh.close()
				continue
			#}}
			newfile = conffile + '.new'
			bakfile = conffile + '.bak'
			model = None
			if os.path.isfile(conffile): #{{
				# directory is marked protected, don't overwrite
				# existing files.
				if protected: continue

				fh = openOut(newfile, model=conffile)
				model = conffile
			#}
			elif fstat: #{
				fh = openOut(newfile,
					uid		= fstat.st_uid,
					gid		= fstat.st_gid,
					mode	= fstat.st_mode,
				)
			#}
			else: #{
				fh = openOut(newfile)
			#}}
			fh.write(outstring)
			fh.close()
			if model: os.rename(conffile, bakfile)
			os.rename(newfile, conffile)
		#}
	#}
	if cfgchanges: #{
		fh = openOut(cfgfile)
		fh.write('''#
# CSADMIN Configured Files
# %s
# The files marked as True have been created by the routine
# Csys.writeTemplates() and will not be modified in subsequent
# runs of that routine (usually called from csadmin).
#
# If for some reason, you need to replace any of these files with
# the ones from the templates, simply remove the line below.
#
''' % cfgfile 
		)
		cfg.rewrite(fh)
	#}
#} writeTemplates

import time

class Logger(CSClass): #{
	'''A simple logger'''

	_attributes = dict(
		package		= '',
		hostname	= Config.hostname,
		progname	= Config.progname.replace('.py', ''),
		logfile		= '',
		logfh		= '',
		mode		= 0600,
		user		= None,
		uid			= None,
		gid			= None,
		_pid		= os.getpid(),
	)
	def __init__(self, package, **kwargs): #{
		CSClass.__init__(self, **kwargs)
		self.package	= package
		if not self.logfile: #{
			self.logfile	= os.path.join(
				sys.prefix,
				'var',
				'%s/%s.log' % (self.package, self.progname)
			)
		#}
		if not hasattr(self.logfh, 'write'): #{
			self.logfh		= open(self.logfile, 'a', buffering=0)
			if os.getuid() != 0: self.user = self.uid = self.gid = None
			if self.user: #{
				if not isinstance(self.user, Csys.Passwd.Passwd): #{
					self.user = Csys.Passwd.getpwnam(self.user)
				#}
				self.uid, self.gid = self.user.uid, self.user.gid
			#}
			if not self.uid is None: os.chown(self.logfile, self.uid, self.gid)
			try: os.chmod(self.logfile, self.mode)
			except OSError: pass
		#}
	#} __init__

	def write(self, msg, logtype='info'): #{
		'''Write log file message in syslog format'''
		dt = time.strftime('%b %e %T')
		fh = self.logfh
		fh.write('%s %s <%s> %s[%d]: %s\n' %
			(
				dt,
				self.hostname,
				logtype,
				self.progname,
				self._pid,
				msg.rstrip(),
			)
		)
		fh.flush()
	#} write

	def close(self): #{
		if self.logfh: self.logfh.close()
	#} close

#} class Logger

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

timefmt = '%a %b %e %T %Z %Y'

class FileInfo(Csys.CSClass): #{
	'''Slight extension of system stat'''
	_attributeList = (
		# ('fname'	, '',		str),
		('type'		, 'R',		str),
		('islink'	, 0,		int),
		('isdir'	, 0,		int),
		('isfile'	, 0,		int),
		('suid'		, 0,		int),
		('sgid'		, 0,		int),
		('st_mode'	, 0,		int),
		('st_ino'	, 0,		int),
		('st_dev'	, 0,		int),
		('st_nlink'	, 0,		int),
		('st_uid'	, 0,		int),
		('st_gid'	, 0,		int),
		('st_size'	, 0,		int),
		('st_mtime'	, 0,		int),
		('st_ctime'	, 0,		int),
		('md5'		, '',		str),
		('sha'		, '',		str),
		('changed'	, 0,		int),
	)
	_len_attributeList = len(_attributeList)

	_attributes = {
	}
	_attributeNames = []
	for k, v, f in _attributeList: #{
		_attributes[k] = v
		_attributeNames.append(k)
	#}
	# maximum size to read in a block
	_maxblocksize = 1024*1000
	def __init__(self, fname=None, calcsums=False, **kwargs): #{
		if fname: #{
			Csys.CSClass.__init__(self, **kwargs)
			self.fname		= fname
			# kludge to work around djbdns generator.
			if self.type == '+pugs12-inamc': self.type = 'R'
			st				= os.lstat(fname)
			self.st_mode	= st_mode = st.st_mode
			self.st_ino		= st.st_ino
			self.st_dev		= st.st_dev
			self.st_uid		= st.st_uid
			self.st_gid		= st.st_gid
			self.islink		= int(stat.S_ISLNK(st_mode))
			if self.islink:	return
			self.isdir		= int(stat.S_ISDIR(st_mode))
			if self.isdir:	return
			self.isfile		= int(stat.S_ISREG(st_mode))
			self.suid		= int(st_mode & stat.S_ISUID)
			self.sgid		= int(st_mode & stat.S_ISGID)
			if self.suid or self.sgid: self.type = 'R'
			self.st_nlink	= st.st_nlink
			self.st_size	= st.st_size
			self.st_mtime	= int(st.st_mtime)
			self.st_ctime	= int(st.st_ctime)
			if self.type == 'R' and self.st_size > 0 and calcsums: self.calcsums()
		#}
	#} __init__

	def __cmp__(self, othr): #{
		if self.isfile and self.type == 'R': return(cmp(
			(self.st_mode, self.st_uid, self.st_gid, self.st_size, self.md5, self.sha),
			(othr.st_mode, othr.st_uid, othr.st_gid, othr.st_size, othr.md5, othr.sha),
		))
		return(cmp(
			(self.st_mode, self.st_uid, self.st_gid),
			(othr.st_mode, othr.st_uid, othr.st_gid),
		))
	#} __cmp__

	def to_python(self, fname, s): #{
		'''Create record from __str__ string'''

		vals = s.split('\t')
		if len(vals) >= self._len_attributeList: #{{
			obj = FileInfo(None)
			obj.fname = fname
			cols = obj.__dict__
			for i in range(0, self._len_attributeList): #{
				k, v, f = self._attributeList[i]
				try: #{{
					cols[k] = f(vals[i])
				#}
				except: #{
					print 'to_python(%s)' % s
					print '\t%d %s %s' % (i, k, vals[i])
					raise
				#}}
			#}
		#}
		else: #{
			import cPickle as pickle
			# this is for backwards compatibility.
			obj = pickle.loads(s)
			cols = obj.__dict__
			# convert bools to int
			for key in (
				'islink',
				'isdir',
				'isfile',
				'suid',
				'sgid',
				'changed'
			): #{
				# use int(bool()) to take care of None
				cols[key] = int(bool(cols[key]))
			#}
		#}}
		return obj
	#} to_python

	to_python = classmethod(to_python)

	def __str__(self): #{
		'''tab delimited string for storage'''
		cols = self.__dict__
		vals = [str(cols[x]) for x in self._attributeNames]
		return '\t'.join(vals)
	#} __str__

	def calcsums(self): #{
		'''Calculate md5 and sha-1 digests for file'''
		st_size = self.st_size
		if st_size > 0: #{{
			blksize = min(st_size, self._maxblocksize)
			st_md5 = md5()
			st_sha = sha()
			fh = open(self.fname)
			while(st_size > 0): #{
				s = fh.read(blksize)
				st_md5.update(s)
				st_sha.update(s)
				st_size -= blksize
			#}
			self.md5	= st_md5.hexdigest()
			self.sha	= st_sha.hexdigest()
		#}
		else: self.md5 = self.sha = '' #}
	#} calcsums

	def uniqueID(self): #{
		'''Unique ID in File System'''
		return((self.st_ino, self.st_dev))
	#} uniqueID

	def prettyprint(self): #{
		'''Pretty output'''
		from Csys.Edits import i2s

		fmt = (
			'%(fname)s\n'
			'    size %(st_size)s mode 0%(st_mode)o'
			' uid %(st_uid)s gid %(st_gid)s'
			' suid %(suid)s sgid %(sgid)s\n'
			'  mtime: %(st_mtime)s\n'
			'  ctime: %(st_ctime)s\n'
			'    md5: %(md5)s\n'
			'  sha-1: %(sha)s'
		)
		prmap			= Csys.CSClassBase(self.__dict__)
		if prmap.st_size: prmap.st_size = i2s(prmap.st_size)
		prmap.st_uid	= uidname(prmap.st_uid)
		prmap.st_gid	= gidname(prmap.st_gid)
		try: prmap.st_mtime = time.strftime(timefmt, time.localtime(self.st_mtime))
		except: prmap.st_mtime = ''

		try: prmap.st_ctime = time.strftime(timefmt, time.localtime(self.st_ctime))
		except: prmap.st_ctime = ''

		val = fmt % prmap.__dict__
		return val
	#} prettyprint

#} class FileInfo

# from the python library writeup.
def import_dotted(name): #{
	'''Import xxx.yyy.zzz returning the zzz component'''
	mod = __import__(name)
	components = name.split('.')
	for component in components: #{
		mod = getattr(mod, component)
	#}
	return mod
#} import_dotted

_dotSlash = re.compile(r'^\./')

def find(dir, depth=0, maxdepth=0, xdev=None, calcsums=False, noErrors=True, skipDirs=[]): #{
	'''Similar to system find command except that it returns
	FileInfo objects which may be tested by the calling program.

	The calcsums option is passed through to FileInfo to have it
	calculate the md5 and sha1 digests.

	Setting the noErrors option to True causes this to raise
	errors in case of permissions or missing files.

	The FileInfo object will have a ``depth'' attribute which may
	be used for mindepth calculations
	'''
	if dir not in skipDirs: #{
		try: #{{
			depth += 1
			if not isinstance(dir, FileInfo): #{
				dir = FileInfo(dir, calcsums=calcsums)
				dir.depth = depth
			#}
			dirname = dir.fname
			# print 'find(%s)' % dirname
			if not dirname == '.': #{
				# print 'yield >%s<' % dir.fname
				yield dir
			#}
			if xdev and depth == 1: xdev = dir.st_dev
			if not xdev or dir.st_dev == xdev: #{
				entries = sorted(os.listdir(dirname))
				for entry in entries: #{
					if maxdepth and depth > maxdepth: break
					p = FileInfo(_dotSlash.sub('', os.path.join(dirname, entry)), calcsums=calcsums)
					p.depth = depth
					if p.isdir: #{{
						if p.fname not in skipDirs: #{
							for p in find(p, depth, maxdepth, xdev, noErrors, skipDirs): #{
								yield p
							#}
						#}
					#}
					else: #{
						yield p
					#}}
				#}
			#}
		#}
		except: #{
			if not noErrors: raise
		#}}
	#}
#} def find

__doc__ = detab(__doc__) # map tabs to spaces with tab stops at 4

if __name__ == '__main__': #{
	sys.stdout = sys.stderr
	print 'OK'
	print 'prefix: ', Config.prefix
	import pdb
	print 'sendmail: ', Config.sendmail
	# pdb.set_trace()
	# system('date')
	# sys.exit(0)
	rc = run('ls -l %s' % ' '.join(( Config.bash, Config.rpm )))
	print rc
	fh = popen('cat /etc/resolv.conf', bufsize=0)
	print fh.read()
	print Config.rpm
	print '---'
	for line in popen('cat /etc/resolv.conf', bufsize=0):
		print line.rstrip()
	opt = '''a b, c,
		d e f,
		g h i
	'''
	opt = ''
	print COMMA_SPACES.split(opt.strip())
	cfgFile = os.path.join(Csys.prefix, 'etc/swatch/swatch.conf')
	cfg = ConfigParser(cfgFile)
	print cfg.getLines('swatch', 'watchlogs')
	sys.exit(0)
	print 'list2dict: ', list2dict((1, 2, 3, 4))
	for p in find('/', maxdepth=3, xdev=True, noErrors=True):
		if p.depth >= 0: print '>%d< %s' % (p.depth, p.fname)
	print Config.l_prefix
	print Config.sendmail
	print Config.hostname
	print Config.ostype
	print Config.os_release
	print Config.byteorder
	d = {'one':2, 'two':4}
	D = CSClassDict(d)
	print d
	D.key = 'val'
	D.one = 5
	setattr(D, 'three', 3)
	print getattr(D, 'three')
	print D.dumpAttrs()
	sys.exit(0)
	print __doc__
	print '>%s<' % rmComments('''This is uncommented
	# This is a test.
	// And a C++ comment
	/* and this is more 
	stuff done with C style comments
	*/
	/* second C comments */
	This // is # a test
	and this is real as well
	''', all=True, wantarray=False)
	# logger = Logger(package = '/tmp', progname='testing')
	# logger.write('more testing', logtype='debug')
#}
