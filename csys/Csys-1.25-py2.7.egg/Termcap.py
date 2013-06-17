#

__doc__='''Termcap utilities

$Id: Termcap.py,v 1.4 2011/10/05 22:50:45 csoftmgr Exp $'''

__version__='$Revision: 1.4 $'[11:-2]

import os, re, sys, Csys
from Csys.Edits import termcap2chars

_Count = 0
class _LineDict(object): #{
	def __init__(self, line): #{
		global _Count
		_Count += 1
		self.nmbr = _Count
		self.line = line
	#}
	def __cmp__(self, other):
		return cmp(self.nmbr, other.nmbr)

#} _lineDict

def _file2string(fname, wantarray=False, pattern=None): #{
	patterns = (
		(re.compile(r'\\\n', re.DOTALL),	''),
		(re.compile(r':\t*:'),				':'),
	)
	lines = {}
	if hasattr(fname, 'readlines'): fh = fname
	else: fh = open(fname)
	for line in fh: #{
		line = line.rstrip()
		if not line.startswith('#'): #{
			line = _LineDict(line)
			lines[line.nmbr] = line
		#}
	#}
	lines = lines.values()
	lines.sort()
	body = '\n'.join([line.line for line in lines])
	# print body
	for pat, repl in patterns: #{
		body = pat.sub(repl, body)
	#}
	if wantarray or pattern: #{
		body = body.split('\n')
		if pattern: body = Csys.grep(pattern, body)
		return body
	#}
	return body
#} _file2string

_termcapBodies = {}

class Termcap(Csys.CSClass): #{
	_attributes = {
		'term'		: os.environ.get('TERM', ''),
		'termcap'	: os.environ.get('TERMCAP', '/etc/termcap'),
	}
	_boolPattern	= re.compile(r'^\w\w$')
	_numPattern	= re.compile(r'^(\w\w)#(.*)')
	_strPattern	= re.compile(r'^(\w\w)=(.*)')

	def __init__(self, term=None, termcap=None, expand=True): #{
		Csys.CSClass.__init__(self)
		if term: self.term = term
		if termcap: self.termcap = termcap
		cols = self.__dict__
		termcap = self.termcap
		if (not os.path.isfile(termcap)
			and not re.compile(r'(^|\|)%s[:\|]' % self.term).search(termcap)
		): termcap = '/etc/termcap'

		if os.path.isfile(termcap): #{{
			# print 'term: ', self.term
			termcaps = _termcapBodies.get(termcap)
			if not termcaps: #{
				termcaps = _file2string(termcap, wantarray=True)
				_termcapBodies[termcap] = termcaps
			#}
			pattern = r'(^|\|)%s[:\|]' % self.term
			try: #{{
				entries = Csys.grep(pattern, (termcaps[:]))
				self.entries = entries[0]
			#}
			except IndexError, e: #{
				self.entries = ''
				# print 'pattern: ', pattern
				# print 'termcaps: ', termcaps
				# print 'termcap: ', termcap
				# print 'entries: ', entries
				# raise
			#}}
		#}
		else: #{
			self.entries = termcap
		#}}
		for field in [f.strip() for f in self.entries.split(':') if f.strip()]: #{
			# print 'field: ', field
			if self._boolPattern.match(field): #{
				cols[field] = True
				continue
			#}
			R = self._numPattern.match(field)
			if R: #{
				cols[R.group(1)] = int(R.group(2))
				continue
			#}
			R = self._strPattern.match(field)
			if R: #{
				k, v = R.group(1), R.group(2)
				if expand: v = termcap2chars(v)
				cols[k] = v.rstrip(':')
			#}
		#}
		if 'tc' in cols: #{
			# print 'getting >%s<' % self.tc
			tc = Termcap(term=self.tc, termcap=self.termcap, expand=expand)
			for field, value in tc.__dict__.items(): #{
				if not field in cols: #{
					# print 'updating >%s<' % field
					cols[field] = value
				#}
			#}
		#}
		if 'pc' in cols and cols['pc'] == '': self.pc = '\0'
		if 'bc' in cols and cols['bc'] == '': self.bc = '\b'
	#} __init__

	def __getattr__(self, name): #{
		'''This is largely to provide default behavior for old
		perl programs which reference undefined attributes'''
		cols = self.__dict__
		# strip leading "tc_" to permit things like TC.tc_is
		# where TC.is would give a syntax error.
		name = name.lstrip('tc_')
		if name == 'init_string': name = 'is'
		return cols.get(name, '')
	#}
#} Termcap

# cache for termcap entries
_termcapEntries = {}

def getTermcap(term=None, termcap=None, expand=True): #{
	'''Get termcap entry and cache it'''
	key = repr((term, termcap, expand))
	tc = _termcapEntries.get(key) or Termcap(term, termcap, expand)
	_termcapEntries[key] = tc
	return tc
#} getTermcap

if __name__ == '__main__': #{
	print 'OK'
	termcap = Termcap(
		term = 'hp4mplus-dx',
		termcap = '/csoft/etc/cssysvlp/termcap'
	)
	print termcap.dumpAttrs()
	print '>%s<' % termcap.ti
	sys.exit(0)
	print termcap.ae
	body = _file2string('/csoft/etc/cssysvlp/termcap',
		wantarray=True,
		pattern = r'\|nec860\|',
	)
	for line in body:
		print line
		print ''
#}
