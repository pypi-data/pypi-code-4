# Csys.Edits

import re, string, sys, Csys
from FixedPoint import FixedPoint

__version__ = '1.1'

_Mac_Table = dict([ (name, len(name)) for name in (
	"MacDonald",
	"MacKay",
	"Macaque",
	"Macassar",
	"Macbeth",
	"Macdonald",
	"Macedon",
	"Macedonia",
	"Machiavelli",
	"Machination",
	"Machine",
	"Machinelike",
	"Machinery",
	"Machismo",
	"Mackay",
	"Mackerel",
	"Mackey",
	"Mackinac",
	"Mackintosh",
	"Macmillan",
	"Macrame",
	"Macromolecular",
	"Macromolecule",
	"Macrophage",
	"Macroprocessor",
	"Macroscopic",
	"Macrostructure",
)])

class Error(Exception): #{
    '''Base class for Csys.Edits exceptions'''
    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__
#} class Error

class BadData(Error): #{
	def __init__(self, field, msg): #{
		'''Bad Data in field'''
		Error.__init__(self, msg)
		self.field	= field
		self.msg	= msg
	#}
#} BadData

def uplow(str, n=None) : #{
	'''Capitalize including handling proper names'''
	_delim = " \t/.,';!@#$%^&()-=+[]*?\"|"
	while str : #{ strip leading delimiters
		if _delim.find(str[0]) < 0: break
		str = str[1:]
	#}
	while str : #{ strip trailing delimiters
		if _delim.find(str[-1:]) < 0 : break
		str = str[:-1]
	#}
	if n is None :
		n = len(str)
	else :
		str = str[:n] # truncate to length n
		# The result will always be less than or equal to the
		# length here since split compresses white space.

	if not str : return str # nothing left to do
	words = str.split() # split on whitespace
	wordsOut = []
	for word in words : #{
		while  True : #{ break to get out
			if len(word) <= 2 or word in _Mac_Table: break
			word = word[:1].upper() + word[1:] # uppercase first letter
			if word[:2] == 'De'				: break # take De...  literally
			word = word[:1] + word[1:].lower() # make rest lower case
			i = 0
			# scotts last names
			if word[:3] == 'Mac'	: i = 3
			elif word[:2] == 'Mc'	: i = 2
			try:
				if i: word = word[:i] + word[i].upper() + word[i+1:]
			except: pass
			break
		#}
		wordsOut.append(word)
	#}
	return(' '.join(wordsOut))
#} uplow

def phone(phonein) : #{
	'''phone(string) -> (area) nnn-nnnn'''
	if phonein: #{
		phonein = str(phonein).strip()	# strip leading and trailing white space
		phonein = re.sub(r'[-.()\s]', '', phonein) # remove strange characters
		phonein = phonein[:10] # truncate to ten characters
		phonein = phonein[:-4] + '-' + phonein[-4:] # add - before final four
		if len(phonein) > 8 :
			phonein = '(%s) %s' % ( phonein[:3] , phonein[3:] )
	#}
	return phonein
#} phone

# Translation table for characters to the phone pad keys
alpha2numbs = string.maketrans(
	'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
	'2223334445556667777888999922233344455566677778889999')

def telenum(phonein) :
	'''telenum(phonein) -> all numeric phone number'''
	return(phone(phonein.translate(alpha2numbs)))

def allup(str) : return(str.upper())

def lower(str) : return(str.lower())
_txt1 = (
	"One ", "Two ", "Three ", "Four ", "Five ", "Six ", "Seven ", "Eight ",
	"Nine ", "Ten ", "Eleven ", "Twelve ", "Thirteen ", "Fourteen ",
	"Fifteen ", "Sixteen ", "Seventeen ", "Eighteen ", "Nineteen ",
	"Twenty "
)
_txt2 = (
	"Twenty ", "Thirty ", "Forty ", "Fifty ", "Sixty ", "Seventy ",
	"Eighty ", "Ninety ", "One Hundred "
)

def amttext(n=0, buf='') : #{
	'''amttext(n, buf) -> amount as text'''
	if n == 0 : return buf
	if n <= 20 :
		return buf + _txt1[n - 1]

	if n <= 100 :
		tens	= int(n / 10)
		units 	= int(n % 10)
		buf = buf + _txt2[tens - 2]
		return amttext(units, buf);

	if n < 10000 :
		hundreds	= int(n / 100)
		rem			= int(n % 100)
		buf			= amttext(hundreds, buf) + 'Hundred '
		return amttext(rem, buf);

	if n < 1000000L :
		thousands	= long(n / 1000);
		rem			= long(n % 1000);
		buf = amttext(thousands, buf) + 'Thousand '
		return amttext(rem, buf)

	if n < 1000000000L :
		millions	= long(n / 1000000);
		rem			= long(n % 1000000);
		buf = amttext(millions, buf) + 'Million '
		return amttext(rem, buf)

	if n < 1000000000000L :
		billions	= long(n / 1000000000L);
		rem			= long(n % 1000000000L);
		buf = amttext(billions, buf) + 'Billion '
		return amttext(rem, buf)

	return('***TILT***')
#} amttext

def spellamt(amt=0, currency='Dollars') : #{
	'''spellamt(longint, currency) -> spelled out amount'''
	n = long(long(amt) * 100L + 0.5)

	if n <= 0 :
		return("**VOID**VOID**VOID**VOID**VOID**VOID**VOID**VOID**")
	dollars	= long(n / 100);
	cents	= int(n % 100);

	if dollars == 0 :
		buf = '***Zero '
	else :
		buf = '***' + amttext(dollars)

	buf = buf + 'and '
	if cents > 0 :
		buf = buf + "%02d/100" % cents
	else :
		buf = buf + 'No/100'

	return ('%s %s***' % (buf, currency))
#} spellamt

def amttxt(amt) : return spellamt(amt)

_signpat	= re.compile(r'^(-*)(.*)$')

def d2s(str) : #{
	'''d2s(str) -> [-]nnn,nnn,nnn.nn'''
	str = '%s' % FixedPoint(str)	# convert to float string
	rc, str = (str[-3:], str[:-3])
	regex	= _signpat.search(str)
	sign	= regex.group(1)
	str		= regex.group(2)
	while len(str) > 3 :
		rc = ',%s%s' % ( str[-3:], rc )
		str = str[:-3]

	return(sign + str + rc)
#} d2s

def amtcomma(str) : return(d2s(str))

def i2s(str) : #{
	'''i2s(str) -> [-]nnn,nnn,nnn'''
	str = '%d' % long(str)	# convert to float string
	regex	= _signpat.search(str)
	sign	= regex.group(1)
	str		= regex.group(2)
	rc		= ''
	while len(str) > 3 :
		rc = ',%s%s' % ( str[-3:], rc )
		str = str[:-3]

	return(sign + str + rc)
#} i2s

def ssn(str, n=None) : #{
	'''Return ssn as nnn-nn-nnnn'''
	if n is None : n = 11 # len('nnn-nn-nnnn')
	str = str.replace('-', '') # remove embedded dashes
	str = str[:3] + '-' + str[3:5] + '-' + str[5:]
	return(str[:n])
#} ssn

def detab(src, ts=4): #{
	'''Expand tabs to spaces with tab stops at ts intervals'''
	assert ts > 0, 'detab: ts tab stop must be > 0'
	lines = src.split('\n')
	outlines = []
	for src in lines: #{
		dst = ''
		while len(src): #{
			n = src.find('\t')
			if n == -1: #{
				dst += src
				break
			#}
			dst += src[:n] + ' ' # at least one space
			while(len(dst) % ts) : dst += ' '
			src = src[n+1:]
		#}
		outlines.append(dst)
	#}
	return "\n".join(outlines)
#} detab

def yesno(inp): #{
	'''Yes or No returned in upper case'''
	inp = str(inp)[:1].upper()
	if inp in ('Y', 'N'): return(inp)
	raise ValueError
#} yesno

_ipaddrPattern = re.compile(r'^([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$')

def ipaddr(ip): #{
	'''Simpleminded IP edit'''
	if ip: #{
		R = _ipaddrPattern.match(str(ip))
		if not R:
			raise BadData('ipaddr', 'ipaddr: invalid IP >%s<' % ip)
		for i in R.groups(): #{
			i = int(i)
			if not 0 <= i <= 255:
				raise BadData('ipaddr', '>%s<: octet %d out of range' % (ip, i))
		#}
	#}
	return ip
#} ipaddr

_intPattern = re.compile(r'^([-+]{0,1}[0-9]+)')

def str2int(value): #{
	'''Convert leading digits of string to integer'''
	try: rc = int(value)
	except ValueError: #{
		R = _intPattern.match(str(value))
		if R: rc = int(R.group(1))
		else: rc = 0
	#}
	return rc
#} str2int

# Termcap string parsing routines

def _myoct(R): #{
	# print 'myoct: ', R.group(1)
	i = chr(eval(R.group(1)))
	return i
#}
def _myhex(R): #{
	# print 'myhex: ', R.group(1)
	i = chr(eval(R.group(1)))
	return i
#}
def _my999(R): return (chr(R.group(1)) & 0177)
def _myord(R): return chr(ord(R.group(1)) & 31)
def _mychr(R): #{
	# print 'mychr: ', R.group(1)
	return (R.group(1))
#}
_stringPatterns = (
	(re.compile(r'\\E'),								'\033'),
	(re.compile(r'\200'),							chr(0)),# NUL character
	(re.compile(r'\\(0\d\d)'),						_myoct), # octal
	(re.compile(r'\\(0x[0-9A-Fa-f][0-9A-Fa-f])'),	_myhex), # hex
	(re.compile(r'\\(\d\d\d)'),						_my999),
	(re.compile(r'\\n'),								'\n'),
	(re.compile(r'\\r'),								'\r'),
	(re.compile(r'\\t'),								'\t'),
	(re.compile(r'\\b'),								'\b'),
	(re.compile(r'\\f'),								'\f'),
	(re.compile(r'\\\^'),							'\377'),
	(re.compile(r'\^\?'),							'\177'),
	(re.compile(r'\^(.)'),							_myord), # ctrl
	(re.compile(r'\377'),							'^'),
	(re.compile(r'\\(.)'),							_mychr),
) # _stringPatterns

def termcap2chars(value, debug=False): #{
	'''Convert termcap encoded string to binary characters'''
	i = 0
	for pat, repl in _stringPatterns: #{
		i += 1
		try: #{{
			value = pat.sub(repl, value)
		#}
		except Exception, e: #{
			if debug: #{
				print 'error pattern %d' % i
				print 'error = >%s< i = %d value = >%s<' % (e, i, value)
			#}
		#}}
	#}
	return value
#} termcap2chars

_specialChars = re.compile(r'''(['";])''')

def sqlrepr(str): #{
	'''Convert string to SQL safe string'''
	str = "'" + _specialChars.sub(r'\\\1', str) + "'"
	return str
#} sqlrepr

if __name__ == '__main__' :
	print sqlrepr(r'''t'est;s""t\\uff'''); sys.exit(0)
	d = detab('ab\tcd\t\tef')
	print str2int('13.7')
	print 'n = %d >%s<' % (len(d), d)
	print '12345678901234567890'
	print d
	print ipaddr('192.136.111.207')
