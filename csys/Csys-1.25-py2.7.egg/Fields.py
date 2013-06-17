#
__doc__='''Celestial Software's Field Utilities

$Id: Fields.py,v 1.6 2009/11/25 02:11:47 csoftmgr Exp $'''

__version__='$Revision: 1.6 $'[11:-2]

fdescs = {}		# dictionary of field descriptions

import os, sys, FixedPoint, re, time
from Csys.Dates import strdate, day, getdate, DF_SQLDATE, today, dayfrom, DF_MM_DD_YYYY
import Csys, Csys.Edits

fieldTypes	= {
	1					: 'char',
	'Char'				: 1,
	3					: 'decimal',
	'Decimal'			: 3,
	12					: 'varchar',
	'VarChar'			: 12,
	4					: 'int',
	'Int'				: 4,
	9					: 'date',
	'Date'				: 9,
	# PostGresql types
	'CHARACTER VARYING'	: 12,
	'CHARACTER'			: 1,
	'NUMERIC'			: 3,
	'INT'				: 4,
	'DATE'				: 9,
} # fieldTypes

_chartype = type('')

# make sure there are all upper and all lower keys.
for _ftype in fieldTypes.keys(): #{
	if type(_ftype) == _chartype: #{
		key = _ftype.lower()
		fieldTypes[key] = fieldTypes[_ftype]
		key = _ftype.upper()
		fieldTypes[key] = fieldTypes[_ftype]
	#}
#} _ftype

_charTypes = ( fieldTypes['Char'], fieldTypes['VarChar'] )

editTypes = {
	'allup':	Csys.Edits.allup,
	'ipaddr':	Csys.Edits.ipaddr,
	'lower':	Csys.Edits.lower,
	'phone':	Csys.Edits.phone,
	'spellamt':	Csys.Edits.spellamt,
	'ssn':		Csys.Edits.ssn,
	'str2int':	Csys.Edits.str2int,
	'telenum':	Csys.Edits.telenum,
	'uplow':	Csys.Edits.uplow,
	'yesno':    Csys.Edits.yesno,
	None:		None,
} # editTypes

_hasSingleQuotes = re.compile(r'^"(.*)"$')

def _fixSingleQuotes(regexobj): #{
	'''Routine to fix embedded single quotes'''
	s = regexobj.group(1)
	s = s.replace("'", r"\'")
	return ("'%s'" % s)
#} _fixSingleQuotes

class FieldDesc(Csys.CSClass): #{
	'''Field Definitions
	
	This class describes the individual field attributes, and is
	referenced extensively throughout this system.

	Attributes:
		dbh		Database Connection instance
		cursor	Database connection cursor
		schema	schema in database (default 'public')
		rname	record (table) name
		lname	Field (column) name.  This will be lower case
		pname	perlish name rname_lname for unique naming and
				quick access.  This and the next attribute,
				selname, may be used as keys to the fdescs
				dictionary for quick reference to the fdesc
				descriptions, but with (dbh, schema) as part
				of the key, and a short version with just pname.
		
		editsub	reference to edit subroutine which will be
				called fdesc.editsub(db_data_type)

		displen	The length of the field displayed.

		scale	This is the number of characters to the right of
				the decimal point for decimal fields.

		chartype This will be set to the character type in
				character fields (char and varchar), and None on
				others.  It's used primarily as a quick check to
				see whether character processing needs to be
				performed.

		fmt		String format for normal output, normally '%s'

		sortfmt	String format for sorting and display.  This will
				be set to give a field of width displen with
				appropriate justification.  Numeric fields will
				have leading zeres.

		iskey	True if field is key (only single field keys)

		edit	edit function, allup, lower, uplow, phone, ssn

		passwd	Set true to suppress display

		defaultval	Default Value

	methods
		set		Routine to create database field.  Normally this
				is used as db_val = fdesc.set(string)

		set_xxx	Utilities to set attributes above.

	'''
	_attributes = {
		'dbh'			: None,
		'cursor'		: None,
		'schema'		: 'public',
		'rname'			: None,
		'lname'			: None,
		'pname'			: None,
		'sname'			: None,
		'description'	: None,
		'displen'		: None,
		'edit'			: None,
		'editsub'		: None,
		'idkey'			: False,
		'nullok'		: False,
		'precision'		: None,
		'scale'			: None,
		'type'			: 'char',
		'sqldesc'		: None,
		'passwd'		: False,
		'defaultval'	: None,
	}
	def __init__(self, **kwargs): #{
		'''the sqldesc paramater should be an array as
		returned by the DBI metadata containing a list or tuple
		with variables (description, type, displen, servsize,
		precision, scale, nullok)
		'''
		Csys.CSClass.__init__(self, False, **kwargs)
		self._setNames()
	#} __init__

	def _setNames(self): #{
		global fdescs
		if self.lname is None and self.description: #{{
			self.lname = self.description
		#}
		elif not self.description and self.lname: #{
			self.description = self.lname
		#}}

		lname = self.lname
		assert lname is not None, 'fdesc: lname must be defined'
		if self.pname is None: self.pname = '%s_%s' % (self.rname, self.lname)
		if self.sname is None: self.sname = '%s.%s' % (self.rname, self.lname)
		self.key = (self.dbh, self.schema, self.rname, self.lname)

		# set global fdescs to all possible keys.
		for key in (
			self.key,
			(self.rname, self.lname),
			self.sname, self.pname
		): fdescs[key] = self

		if self.edit: self.edit = editTypes[self.edit.lower()]

		description = self.sqldesc
		if description is not None: #{{
			self.__dict__.update(
				dict(zip( ( 'type', 'displen', 'servsize', 'precision',
						'scale', 'nullok'), description[1:] ))
			)
		#}
		else: #{
			self.displen	= int(self.displen)
		#}}
		self._proctype()	# process type and associated fields
	#} _setNames

	def fldlen(self): return self.displen
	def fldtyp(self): return self.type

	_nonePattern = re.compile(r"^'None\s*'$", re.IGNORECASE)

	def sqlQuote(self, val=None): #{
		'''Quote val appropriately for SQL'''
		if val is None: val = self.__dict__.get(val)
		if val is None: val = 'NULL'
		else: #{
			if self.chartype:					val = repr(self.sortfmt % val)
			else:								val = repr(self.fmt % val)
			if self._nonePattern.match(val):	val = 'NULL'
			else: val = _hasSingleQuotes.sub(_fixSingleQuotes, val)
		#}
		return(val)
	#} sqlQuote

	def _setchar(self, inp=''): #{
		'''Set character string limited by length'''
		if inp is None: return None
		if type(inp) != _chartype: inp = str(inp)
		inp = inp.strip()
		if self.edit: inp = self.edit(inp)
		return(inp[:self.displen])
	#} _setchar

	_amtfilter = re.compile(r'^([-+]{0,1}[.\d]+).*')

	def _setamt(self, inp=None): #{
		'''Set Fixpoint'''
		if not isinstance(inp, FixedPoint.FixedPoint): #{
			if not inp: inp = '0.00'
			elif isinstance(inp, ''.__class__): inp = self._amtfilter.sub(r'\1', inp)
		#}
		return(FixedPoint.FixedPoint(inp, precision=self.scale))
	#} _setamt

	_intfilter = re.compile(r'^([-+]{0,1}\d+).*')

	def _setint(self, inp=None): #{
		'''Set Fixpoint'''
		if inp is None: return(0)
		if isinstance(inp, ''.__class__): inp = self._intfilter.sub(r'\1', inp)
		try: #{{
			return(int(inp))
		#}
		except: #{
			return(0)
		#}}
	#} _setint

	def _setdate(self, inp=None): #{
		'''Set Date'''
		if inp == '' or inp == '0000-00-00': imp = None
		elif inp: #{
			datestr = strdate(str(inp)[:10], DF_MM_DD_YYYY)
			inp = (datestr)
		#}
		return(inp)
	#} _setdate

	def _setdefault(self, inp=None): #{
		'''Default set'''
		return(inp)
	#} _setdefault

	def _proctype(self): #{
		'''Set numeric field type, format, and other type related things'''

		cols = self.__dict__

		if type(self.type) == _chartype: #{
			cols['type'] = fieldTypes[self.type.lower()]
		#}
		ftype = self.type

		cols['sortfmt'] = None

		is_char = cols['chartype'] = (ftype in _charTypes)

		if is_char: #{
			cols['fmt']		= '%s'
			cols['sortfmt']	= '%%-%ds' % self.displen
			cols['set']		= self._setchar
		#}
		elif ftype == fieldTypes['Decimal']: #{
			cols['fmt'] = '%%%d.2f' % (self.displen - 5)
			cols['set'] = self._setamt
		#}
		elif ftype == fieldTypes['Int']: #{
			cols['fmt']		= '%%%dd' % self.displen
			cols['sortfmt']	= '%%0%dd' % self.displen
			cols['set']		= self._setint
		#}
		elif ftype == fieldTypes['Date']: #{
			cols['fmt'] = '%-10s'
			cols['set'] = self._setdate
		#}
		else: #{
			cols['fmt'] = cols['sortfmt'] = '%s'
			cols['set'] = self._setdefault
		#}
		if cols['sortfmt'] is None: cols['sortfmt'] = self.fmt

	#} _proctype

	def __setattr__(self, attr, val): #{
		'''Set Attributes with appropriate translation'''
		cols = self.__dict__
		if attr in ('type', 'displen'): #{
			cols[attr] = val
			self._proctype()
		#}
		else: #{
			cols[attr] = val
		#}
		return cols[attr]
	#} __setattr__

	def get(self, key): #{
		'''Return Hash'''
		return(fdesc.fdescs.get(key))
	#} get

	def null_buf(self, buf): #{
		'''Is buffer null'''
		return((buf is None) or (self.chartype and buf.strip() == ''))
	#} null_buf

#} FieldDesc

class DBField(Csys.CSClass): #{
	'''Field instance class'''
	_attributes = {
		'fdesc'	: None,
		'rname'	: None,
		'lname'	: None,
		'set'	: None,
		'val'	: None,
	}
	def __init__(self, fdesc, val=None): #{
		'''Initialize the self. structure'''
		Csys.CSClass.__init__(self)
		self.fdesc	= fdesc
		self.rname	= fdesc.rname
		self.lname	= fdesc.lname
		self.set	= fdesc.set
		if val is None: val = fdesc.defaultval
		self.val	= val
	#} __init__

	def __setattr__(self, attr, val): #{
		'''Set attribute, converting if the attr is val'''
		cols = self.__dict__
		if attr == 'val': #{{
			cols['val'] = self.fdesc.set(val)
			cols['str'] = str(self.val)
		#}
		else: #{
			cols[attr] = val
		#}}
	#} __setattr__

	def set_val(self, newval): #{
		'''Return converted value'''
		return self.fdesc.set(newval)
	#} set_val

	def is_null(self): #{
		val = self.val
		return((val is None) or (self.fdesc.chartype and val.strip() == ''))
	#} is_null

	def __str__(self): return(str(self.val))

	def _mkDBField(self, fdesc, val): return DBField(fdesc, val)

	def _norm(x): #{
		if isinstance(x, DBField): x = x.val
		return(x)
	#}
	def copy(self): return self._mkDBField(self.fdesc, self.val)
	
	__copy__ = __deepcopy__ = copy

	def __nonzero__(self): return(self.val != 0)

	def __neg__(self): return(self._mkDBField(self.fdesc, -self.val))

	def __abs__(self):
		if self.val > 0: return self.copy()
		else: return -self

	def __add__(self, other): #{
		other = norm(other)
		return self._mkDBField(self.fdesc, self.val + other)
	#}
	__radd__ = __add__

	def __sub__(self, other): #{
		other = norm(other)
		return self._mkDBField(self.fdesc, self.val - other)
	#}
	def __rsub__(self, other): return (-self) + other

	def __mul__(self, other): #{
		other = norm(other)
		return self._mkDBField(self.fdesc, self.val * other)
	#}
	__rmul__ = __mul__

	def __div__(self, other): #{
		other = norm(other)
		if other == 0:
			raise ZeroDivisionError("DBField division")
		return self._mkDBField(self.fdesc, self.val / other)
	#}
	def __rdiv__(self, other): #{
		other = norm(other)
		if self.val == 0:
			raise ZeroDivisionError("DBField rdivision")
		return self._mkDBField(self.fdesc, other / self.val)
	#}

	def __mod__(self, other): #{
		other = norm(other)
		if other == 0:
			raise ZeroDivisionError("DBField modulo")
		return self._mkDBField(self.fdesc, self.val % other)
	#}
	def __rmod__(self, other): #{
		other = norm(other)
		if self.val == 0:
			raise ZeroDivisionError("DBField rmodulo")
		return self._mkDBField(self.fdesc, other % self.val)
	#}

	def __float__(self): return(float(self.val))

	def __long__(self): return(long(self.val))

	def __int__(self): return(int(self.val))

	def sgfldptr(self): return(self)

	def sgfldamt(self): return(FixedPoint(self.val, precision=self.scale))

	fgetamt = sgfldamt

	def sgfldchar(self): return(str(self.val)[0])

	def sgfldint(self): return(int(self.val))

	def sgflddate(self): return(self.val)

	def strfld(self): return(str(self.val))

#} class DBField

if __name__ == '__main__': print 'OK'
