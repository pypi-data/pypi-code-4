#!/csrel22/bin/python

# $Header: /vol/cscvs/python-Csys/LDAP/__init__.py,v 1.5 2011/10/05 23:14:07 csoftmgr Exp $
# $Date: 2011/10/05 23:14:07 $

import Csys, os, os.path, sys, re

__doc__ = '''LDAP base utilities

$Id: __init__.py,v 1.5 2011/10/05 23:14:07 csoftmgr Exp $
'''

__version__='$Revision: 1.5 $'[11:-2]

_debug_level	= 0
_debug_file		= sys.stderr

Config = Csys.CSClassBase()

key_val_pattern = re.compile(r'^(\S+)\s+(.*)')
fh = open(os.path.join(Csys.prefix, 'etc/openldap/ldap.conf'))
for line in Csys.rmComments(fh, wantarray=True, pattern='.'): #{
	R = key_val_pattern.match(line)
	if R: #{
		key, val = R.groups()
		if key in ('host', 'base', 'uri'): key = key.upper()
		Config.__dict__[key] = val
	#}
#}

ldap_secret = '/etc/ldap.secret'

Config.password = None
try: #{{
	fh = open(ldap_secret)
	passwd = fh.readline().rstrip()
	fh.close()
	Config.password = passwd
#}
except: Config.password = None #}

BASE	= Config.BASE

import ldap, ldap.modlist

connections = {}

class LDAP(Csys.CSClass): #{
	_cols = Config.__dict__
	_attributes = {
		'BASE'				: BASE,
		'HOST'				: _cols.get('HOST'),
		'PORT'				: _cols.get('PORT', 389),
		'password'			: Config.password,
		'BINDDN'			: _cols.get('BINDDN'),
		'SIZELIMIT'			: _cols.get('SIZELIMIT'),
		'TIMELIMIT'			: _cols.get('TIMELIMIT'),
		'DEREF'				: _cols.get('DEREF'),
		'SASL_MECH'			: _cols.get('SASL_MECH'),
		'SASL_REALM'		: _cols.get('SASL_MECH'),
		'SASL_AUTHCID'		: _cols.get('SASL_AUTHCID'),
		'SASL_AUTHZID'		: _cols.get('SASL_AUTHZID'),
		'SASL_SECPROPS'		: _cols.get('SASL_SECPROPS'),
		'TLS_CACERTDIR'		: _cols.get('TLS_CACERTDIR'),
		'TLS_CERT'			: _cols.get('TLS_CERT'),
		'TLS_KEY'			: _cols.get('TLS_KEY'),
		'TLS_CIPHER_SUITE'	: _cols.get('TLS_CIPHER_SUITE'),
		'TLS_RANDFILE'		: _cols.get('TLS_RANDFILE'),
		'TLS_REQCERT'		: _cols.get('TLS_REQCERT'),
		'URI'				: _cols.get('URI'),
		'rootdn'			: 'cn=manager,' + BASE,
		'connection'		: None,
		'_key'				: None,
		'_bound'			: False,
		'_asManager'		: False,
	}
	def __init__(self, **kwargs): #{
		Csys.CSClass.__init__(self, **kwargs)

		if self.URI: #{
			self.connection = ldap.initialize(self.URI)
			self._key = self.URI
		#}
		else: #{
			self.connection = ldap.open(self.HOST, self.PORT)
			self._key = (self.HOST, self.PORT)
		#}
		connections[self._key] = self
	#}
	def bind(self, dn='', pw=''): #{
		result = self.connection.simple_bind_s(dn, pw)
		self._bound = True
		return result
	#}
	def bindmgr(self, rootdn=None, password=None): #{
		'''Set rootdn, password, and bind to LDAP server'''
		if self._bound and not self._asManager: #{
			self.unbind()
		#}
		rc = True
		if not self._asManager: #{
			if rootdn:		self.rootdn = rootdn
			if password:	self.password = password
			rc = self.bind(self.rootdn, self.password)
			self._asManager = self._bound
		#}
		return rc
	#} bindmgr

	def __del__(self): #{
		if self.connection: self.unbind()
	#}

	def unbind(self): #{
		return
		print dir(self.connection.unbind_s)
		self._bound = self._asManager = False
	#} unbind

	def chkRoot(self, o): #{
		'''Check root entry for organization'''
		# dc = self.BASE.split(',')[0][3:]
		# make sure that we're bound as root
		self.bindmgr()
		base = self.BASE
		dc = ldap.explode_dn(base, True)[0]
		try: #{{
			results = self.connection.search_s(
				base,
				ldap.SCOPE_BASE,
				filterstr='(dc=*)'
			)
		#}
		except: #{
			attrs = ldap.modlist.addModlist({
				'dc'			: [dc],
				'o'				: [o],
				'objectClass'	: ['top', 'organization', 'dcObject'],
			})
			results = self.connection.add_s(base, attrs)
		#}}
		mgrresults = self.connection.search_s(
			base,
			ldap.SCOPE_SUBTREE,
			filterstr='(cn=Manager)(objectClass=organizationalRole)'
		)
		if not mgrresults: #{
			attrs = ldap.modlist.addModlist({
				'cn'			: ['Manager'],
				'objectClass'	: ['top', 'organizationalRole'],
			})
			dn = 'cn=Manager,' + base
			mgrresults = self.connection.add_s(dn, attrs)
		#}
		return results
	#} chkRoot

#} class LDAP

# myLDAP = LDAP(**Config.__dict__)

class Entry(Csys.CSClass): #{
	'''Utility class to take a result from an ldap search'''
	_attributes = {
		'dn'			: None,
		'ldap'			: None,
		'connection'	: None,
		'objectClass'	: None,
		'_attrsold'		: {},
		'_attrsnew'		: {},
	} # _attributes

	_noTranslationFields = (
		'dn', 'ldap', 'connection', # 'objectClass',
	)

	def __setattr__(self, attr, value): #{
		'''Set attribute and update _attrsnew dictionary'''
		cols = self.__dict__
		if attr in self._noTranslationFields: #{
			cols[attr] = value
			return
		#}
		if not attr in cols or cols[attr] != value: #{
			cols[attr] = value
			# This will update/create the proper entry in _attrsnew
			if attr[0] != '_': #{
				# convert simple string to a list
				if not hasattr(value, '__delitem__'): value = [ str(value) ]
				values = []
				for val in value: values.append(str(val))
				self._attrsnew[attr] = values
			#}
		#}
	#} __setattr__

	def __init__(self, ldapobj, ldapentry=None, dn=None, objectClass=None): #{
		Csys.CSClass.__init__(self)
		self.dn				= dn
		self.ldap			= ldapobj
		self.connection		= ldapobj.connection
		self.objectClass	= objectClass
		if ldapentry: #{
			self.dn, attrs = ldapentry
			if ldapentry: #{
				self.objectClass = attrs['objectClass']
				self._attrsold = attrs
				self._attrsnew = attrs.copy() # hopefully a deep copy
				cols = self.__dict__
				# These will all be lists
				for key, val in attrs.items(): cols[key] = val[0]
			#}
		#}
	#} __init__

	def get_value(self, attr, ndx=0): #{
		'''Return value indexed into array'''
		return self._attrsnew[attr][ndx]
	#} get_value

	def get_values(self, attr): #{
		'''Return attribute array'''
		return self._attrsnew[attr]
	#} get_values

	def add(self, attrs=None): #{
		'''Add Entry to LDAP'''
		dn			= self.dn
		connection	= self.connection
		if not attrs is None: self._attrsnew = attrs
		self._attrsnew['objectClass'] = self.objectClass
		attrs = ldap.modlist.addModlist(self._attrsnew)
		# print 'add: dn >%s<' % dn
		# print attrs
		if not attrs: return None
		# print 'dn, attrs: ', dn, attrs
		results = connection.add_s(dn, attrs)
		return results
	#} add

	def modify(self): #{
		'''Modify Entry in LDAP'''
		attrs = ldap.modlist.modifyModlist(
			self._attrsold, self._attrsnew,
			ignore_oldexistent=1,
		)
		# print 'dn:', self.dn
		# print 'attrsold', self._attrsold
		# print 'attrsnew', self._attrsnew
		# print 'attrs:', attrs
		if attrs:	results = self.connection.modify_s(self.dn, attrs)
		else:		results = None
		# print results
		return results
	#} add

	def delete(self): #{
		try: return self.connection.delete_s(self.dn)
		except: return None
	#} delete

#} Entry

if __name__ == '__main__': #{
	print 'OK'
	conn = LDAP()
	print conn.BASE
	print conn.password
	print conn.rootdn
	conn.bindmgr()
	print 'bindmgr OK'
	print conn._asManager
	sys.exit(0)
	conn.chkRoot('Celestial Software LLC')
	d1 = dir('')
	d2 = dir([])
	d3 = dir({})
	d2d = {}
	d3d = {}
	for d in d2:
		if d not in d1: d2d[d] = True
	for d in d3:
		if d not in d1: d3d[d] = True

	dboth = {}
	for d in d2d.keys():
		if d in d3d: dboth[d] = True
	for d in d3d.keys():
		if d in d2d: dboth[d] = True

	keys = dboth.keys()
	keys.sort()
	print keys
#}
