#!/csrel22/bin/python

# $Header: /vol/cscvs/python-Csys/LDAP/Passwd.py,v 1.6 2011/10/05 23:12:34 csoftmgr Exp $
# $Date: 2011/10/05 23:12:34 $

import Csys, os, os.path, sys, re
import copy

__doc__ = '''LDAP Passord Utilities

$Id: Passwd.py,v 1.6 2011/10/05 23:12:34 csoftmgr Exp $
'''

__version__='$Revision: 1.6 $'[11:-2]

if os.geteuid() != 0: #{
	sys.stderr.write('You must be root to run this\n')
	sys.exit(0)
#}

from Csys.LDAP import *

import ldap, ldap.modlist

import Csys.Passwd

import Csys.Admin
globalConfig = Csys.ConfigParser(
	Csys.Admin.csadmin_conf
).getDict('customer', asClass=True)
company = globalConfig.company

LDAP		= Csys.LDAP.LDAP()
connection	= LDAP.connection
LDAP.bindmgr() # this needs to be done before chkRoot
LDAP.chkRoot(company)

objectClass = [
	'top',
	'account',
	'posixAccount',
	'shadowAccount',
]
addressObjectClass = [
	'top',
	'organizationalUnit',
]
pubObjectClass = (
	'top',
	'person',
	'inetOrgPerson',
	'organizationalPerson',
	'mozillaAbPersonAlpha',
	'calEntry',
)

ldapbase	= LDAP.BASE
userbase	= 'ou=people,' + ldapbase
peraddrbase	= 'ou=personal_addressbook,' + ldapbase
pubaddrbase	= 'ou=shared_addressbook,' + ldapbase

# This section creates necessary organizationalUnits, adding them if
# they don't exist.  We do it in a try loop in case openldap
# isn't running on this machine.
#
try: #{{
	LDAP.bindmgr()
	_organizationalUnits = (
		'people',
		'personal_addressbook',
		'shared_addressbook',
	)
	for ou in _organizationalUnits: #{
		filter = 'ou=%s' % ou
		# print 'filter >%s<' % filter
		_results = connection.search_s(
			ldapbase,
			ldap.SCOPE_ONELEVEL,
			filterstr='(%s)' % filter,
		)
		if not _results: #{{
			dn = '%s, %s' % (filter, ldapbase)
			# print 'add %s dn=%s' % (ou, dn)

			attrs = ldap.modlist.addModlist({
				'ou'			: [ou],
				'objectClass'	: ['organizationalUnit'],
			})
			_results = connection.add_s(dn, attrs)
		#}}
	#}
#}
except: pass #}

def int2str(value): #{
	try: return(str(int(value)))
	except: return '0'
#} int2str

def addCrypt(pw): return '{CRYPT}' + pw

def delCrypt(pw): return pw.replace('{CRYPT}', '', 1)

fieldmap = [
	# Passwd field      LDAP field              To LDAP     To Passwd
	('user',			'uid',					str,		str),
	('pwd',				'userPassword',			addCrypt,	delCrypt),
	('uid',				'uidNumber',			int2str,	int),
	('gid',				'gidNumber',			int2str,	int),
	('gcos',			'cn',					str,        str),
	('home',			'homeDirectory',		str,        str),
	('shell',			'loginShell',			str,        str),
	('expirationDate',	'shadowExpire',			int2str,	int),
	('disableAfter',	'shadowInactive',		int2str,	int),
	('lastChanged',		'shadowLastChange',		int2str,	int),
	('maxChangeDays',	'shadowMax',			int2str,	int),
	('minChangeDays',	'shadowMin',			int2str,	int),
	('warnBefore',		'shadowWarning',		int2str,	int),
	('shadowFlags',		'shadowFlag',			int2str,	int),
] # fieldmap

def Passwd2LDAP(cols=None, pw=None): #{
	'''return dictionary mapping LDAP keys to Passwd'''
	if pw: cols = pw.__dict__
	ld = {}
	for pwkey, ldkey, f1, f2 in fieldmap: #{
		ld[ldkey] = f1(cols[pwkey])
	#}
	ld['objectClass'] = objectClass
	return ld
#} Passwd2LDAP

def LDAP2Passwd(cols=None, ld=None): #{
	'''return dictionary mapping LDAP keys to Passwd'''
	if ld: cols = ld.__dict__
	pw = {}
	for pwkey, ldkey, f1, f2 in fieldmap: #{
		pw[pwkey] = f2(cols[ldkey][0])
	#}
	return pw
#} LDAP2Passwd

accounts = {}
origaccounts = {}

def get_ldap_accounts(ldapobj=LDAP, uid='*', attr='uid', basedn=userbase): #{
	'''Get accounts matching uid (user name)'''
	connection = ldapobj.connection
	try:
		results = connection.search_s(
			basedn,
			ldap.SCOPE_ONELEVEL,
			filterstr='(%s=%s)' % (attr, uid),
		)
	except: return []
	return results
#} get_ldap_accounts

class Passwd(Csys.Passwd.Passwd): #{
	_attributes = {
		'dn'			: None,
		'_ldapstatus'	: None, # add, modify, delete
		'_ldap'			: LDAP,	# Ldap connection
		'_connection'	: connection,
		'_entry'		: None,	# LDAP result entry
		'_changes'		: None,
		'_processed'	: False,# Boolean that will be when passing all accounts
		'_addressEntry' : None, # Entry for addressbook
		'_pubAddrEntry'	: None, # Entry in public addressbook
	}
	_attributes.update(Csys.Passwd.Passwd._attributes)

	def getChanges(self): #{
		self._changes = ldap.modlist.modifyModlist(
			self._entry._attrsold, self._entry._attrsnew,
			ignore_oldexistent=1,
		)
		if self._changes: return (self.dn, self._changes)
		else: return None
	#} getChanges

	def __init__(self, parent, ldapobj=LDAP, entry=None, forcechange=False, seq=0): #{
		Csys.CSClass.__init__(self)
		self._parent		= parent
		self._ldap			= ldapobj
		self._connection	= ldapobj.connection
		if entry: #{
			entry = self._entry = Csys.LDAP.Entry(self._ldap, entry)
			self.dn			= entry.dn
			cols			= self.__dict__
			cols.update(LDAP2Passwd(entry._attrsnew))
		#}
		else: #{
			self._entry = Csys.LDAP.Entry(self._ldap, objectClass=objectClass)
		#}

		# This will call the inherited routine from Csys.Passwd.Passwd
		self.finishInit(seq, forcechange)
		self._ldapstatus = None
	#} __init__

	def getdn(self): #{
		return 'uid=%s,%s' % ( self.user, userbase )
	#} dn

	def add_LDAP(self, maildomain=None, uri=None): #{
		'''Add new entry to LDAP'''
		entry				= self._entry
		self.dn				= entry.dn	= self.getdn()
		entry.objectClass	= objectClass
		ld					= entry._attrsnew
		cols				= self.__dict__

		for pwkey, ldkey, f1, f2 in fieldmap: #{
			val = cols[pwkey]
			# if it's not already a list, convert it
			if not hasattr(val, '__delitem__'): val = [ f1(val) ]
			ld[ldkey] = val
		#}
		try: #{{
			entry.add()
			self._entry = Csys.LDAP.Entry(
				self._ldap,
				get_ldap_accounts(self._ldap, self.user)[0],
			)
			self.addAddressBook()
			if maildomain and uri: #{
				self.addPubAddressEntry(maildomain, uri)
			#}
			self._ldapstatus = 'add'
			accounts[self.user] = self
		#}
		except ldap.INVALID_SYNTAX, err: #{
			sys.stderr.write('Passwd: add failed on %s\n' % self.user)
			sys.stderr.write('\t%s\n' % self.print_compare_string())
			sys.stderr.write('%s\n' % err)
		except ldap.ALREADY_EXISTS, err: #{
			sys.stderr.write('Passwd: add already exists on %s\n' % self.user)
			sys.stderr.write('\t%s\n' % self.print_compare_string())
			sys.stderr.write('%s\n' % err)
		#}
		#}}
	#} add_LDAP

	def addressDN(self): #{
		dn = 'ou=%s,ou=personal_addressbook, %s' % (self.user, ldapbase) 
		return dn
	#} addressDN

	def addAddressBook(self): #{
		'''Add address book organizational unit'''
		entry				= Csys.LDAP.Entry(
			self._ldap,
			dn				= self.addressDN(),
			objectClass 	= addressObjectClass,
		)
		entry.ou			= self.user
		entry.add()
		self.chkAddressBook(addOK=False)
	#} addAddressBook

	def chkAddressBook(self, addOK=True, maildomain=None, uri=None): #{
		results = get_ldap_accounts(self._ldap, attr='ou', uid=self.user,
			basedn=peraddrbase,
		)
		if results: self._addressEntry = Csys.LDAP.Entry(self._ldap, results[0])
		elif addOK: self.addAddressBook()
		# This will add a shared address book if one exists.
		if maildomain and uri: #{
			self.chkPubAddressEntry(addOK, maildomain, uri)
		#}
	#} chkAddressBook

	def syncPasswd(self, pw, maildomain=None, uri=None): #{
		'''Update from Csys.Passwd object'''
		assert isinstance(pw, Csys.Passwd.Passwd), 'updateFromPasswd pw not Passwd'
		if self.print_compare_string() != pw.print_compare_string(): #{
			entry = self._entry
			cols = self.__dict__
			colspw = pw.__dict__
			for pwkey, ldkey, pw2ldap, ldap2pw in fieldmap: #{
				entry.__setattr__(ldkey, pw2ldap(colspw[pwkey]))
			#}
			entry.modify()
			self._ldapstatus = 'update'
		#}
		entry = self.chkPubAddressEntry(addOK=True, maildomain=maildomain, uri=uri)
		if entry: #{
			# this is tne only thing that can change
			entry.__setattr__('cn', pw.gcos)
			try: entry.modify()
			except: pass
		#}
	#} syncPasswd

	# Delete LDAP entry and any associate fields
	def delete_LDAP(self): #{
		self.chkAddressBook(addOK=False)
		#
		# delete personal addressbook entries and personal
		# addressbook ourganizational unit.
		#
		if self._addressEntry: #{
			results = get_ldap_accounts(self._ldap,
				basedn	= self._addressEntry.dn,
				attr	= 'objectClass',
				uid		= 'person',
			)
			for result in results: result.delete()
			self._addressEntry.delete()
		#}
		self.chkPubAddressEntry(False)
		if self._pubAddrEntry: self._pubAddrEntry.delete()
		self._entry.delete()
	#} delete_LDAP

	def addPubAddressEntry(self, maildomain=None, uri=None): #{
		user = self.user
		gcos = self.gcos
		if gcos and gcos != 'unknown': #{
			dn = 'uid=%s,%s' % (user, pubaddrbase)
			self._pubAddrEntry = entry = Csys.LDAP.Entry(self._ldap,
				dn=dn,
				objectClass=pubObjectClass,
			)
			entry.uid		= user
			entry.cn		= gcos
			entry.mail		= '%s@%s' % (user, maildomain)
			try: #{{
				entry.calFBURL	= uri % user
				entry.add()
			#}
			except: pass #}
			self.chkPubAddressEntry(addOK=False)
		#}
	#} addPubAddressEntry

	def chkPubAddressEntry(self, addOK=True, maildomain=None, uri=None): #{
		'''Add new entry to shared addressbook'''
		user = self.user
		results = get_ldap_accounts(self._ldap, attr='uid', uid=user,
			basedn=pubaddrbase,
		)
		if results: self._pubAddrEntry = Csys.LDAP.Entry(self._ldap, results[0])
		elif addOK: self.addPubAddressEntry(maildomain, uri)
		return self._pubAddrEntry
	#} chkPubAddressEntry

#} class Passwd

def read_LDAP(parent, ldapobj=LDAP): #{
	seq = 0
	accounts	= {}
	results		= get_ldap_accounts(ldapobj) # get all accounts
	for result in results: #{
		seq += 1
		account			= Passwd(parent, ldapobj, result, seq=seq)
		user			= account.user
		accounts[user]	= account
	#}
	return accounts
#} read_LDAP

def getUser(uid, parent=None, ldapobj=LDAP): #{
	result = get_ldap_accounts(ldapobj, uid=uid)
	if result: account = Passwd(parent, ldapobj, result[0])
	else: account = None
	return account
#} getUser

class PasswdAccounts(Csys.Passwd.PasswdAccounts): #{
	_attributes = Csys.Passwd.PasswdAccounts._attributes.copy()

	_attributes.update({
		'ldap'				: LDAP,
		'connection'		: connection,
		'_readaccounts'		: False,
	}) # _attributes

	def __init__(self, ldapobj=LDAP, **kwargs): #{
		Csys.Passwd.PasswdAccounts.__init__(self, **kwargs)
		self.ldap		= ldapobj
		self.connection	= self.ldap.connection
		self.lockupdate = False
		self.ssh		= None,
		self.accts		= read_LDAP(self, self.ldap)
		self.origaccts	= self.accts.copy()
	#} __init__

	def deletedaccts(self): #{
		'''Return deleted account objects'''
		accts = self.accts
		deleted = {}
		# a normal pass through the users will have marked the status
		# as either 'add' or 'update'.
		for k, v, in self.accts.items(): #{
			if v._ldapstatus is None: deleted[k] = v
		#}
		return deleted
	#} deletedaccts

	def changedaccts(self): #{
		'''Return dictionary of accounts with changes'''
		changed = {}
		if self.changes: #{
			for k, v in self.accts.items(): #{
				changes = v.getChanges
				if changes: changed[k] = changes
			#}
		#}
		return changed
	#} changedaccts

	def updateLDAP(self): #{
		'''Update any changed accounts, delete old accounts'''
		pass
	#} updateLDAP

	def addPasswd(self, pw, ldapobj=LDAP, maildomain=None, uri=None): #{
		'''Add an LDAP entry from Csys::Passwd object'''
		assert isinstance(pw, Csys.Passwd.Passwd), 'add_Passwd pw not Passwd'
		account = Passwd(self, ldapobj=ldapobj) # create empty password object
		cols = account.__dict__
		cols.update(pw.__dict__)
		account.add_LDAP(maildomain, uri)
		self.accts[account.user] = account
		return account
	#} addPasswd

#} PasswdAccounts

def read_passwd_shadow(**kwargs): #{
	'''Read all accounts in LDAP'''
	return PasswdAccounts(**kwargs)
#} read_passwd_shadow

def updateLDAP(user, delete=False): #{
	import Csys.Passwd, Csys.LDAP, Csys.LDAP.Passwd

	cfg = Csys.ConfigParser()
	cfg.readfiles([
		os.path.join(Csys.prefix, 'etc/openldap/upd_passwd.conf'),
		os.path.join(Csys.prefix, 'etc/csadmin/useradmin.conf')
	])
	if hasattr(user, 'home'): #{{
		username	= user.user
		home		= user.home
		user.home	= home.replace('/home/', '/homes/')
	#}
	else: #{
		username	= user
		home		= None
	#}}
	for section in cfg.sections(): #{
		if section.startswith('openldap'): #{
			ld = Csys.CSClassBase(cfg.getDict(section))
			LDAP = Csys.LDAP.LDAP(
				BASE	= ld.base,
				URI		= ld.uri,
			)
			try: LDAP.bindmgr(ld.rootdn, ld.password)
			except ldap.SERVER_DOWN, e: #{
				sys.stderr.write(
					'updateLDAP: bind %s dn = %s pw = %s\n'
					'\tbase >%s< uri >%s<\n\t%s\n'
					% (
						section,
						ld.rootdn,
						ld.password,
						ld.base,
						ld.uri,
						e,
					)
				)
				continue
			#}
			ldapacct = Csys.LDAP.Passwd.getUser(username, ldapobj=LDAP)
			try: #{{
				if delete: #{{
					if ldapacct: ldapacct.delete_LDAP()
				#}
				else: #{
					# both these must be defined or neither is useful
					try: maildomain, uri = ld.maildomain, ld.calfburi
					except: maildomain  = uri = None

					if ldapacct: #{{
						ldapacct.syncPasswd(user, maildomain, uri)
					#}
					else: #{
						ldapacct = Csys.LDAP.Passwd.Passwd(None, LDAP)
						ldapacct.__dict__.update(user.__dict__)
						ldapacct.add_LDAP(maildomain, uri)
					#}}
				#}}
			#}
			except: #{
				raise Csys.Error('ldap error %s' % ld.uri)
			#}}
		#}
	#}
	if not home is None: user.home = home
#} updateLDAP

class UserAddMod(Csys.Passwd.UserAddMod): #{
	'''Add LDAP processing to Csys.Passwd.UserAddMod'''

	def useradd(self, execute=False, adminOK=False): #{
		pw = Csys.Passwd.UserAddMod.useradd(self, execute, adminOK)
		if pw: updateLDAP(pw)
	#} useradd

	def usermod(self, execute=False, adminOK=False): #{
		pw = Csys.Passwd.UserAddMod.usermod(self, execute, adminOK)
		if pw: updateLDAP(pw)
	#} usermod

	def userdel(self, execute=False): #{
		pw = Csys.Passwd.UserAddMod.userdel(self, execute, adminOK)
		if execute and pw and self.rc == '0': updateLDAP(pw, delete=True)
	#} userdel

#} class UserAddMod

if __name__ == '__main__': #{
	print 'OK'
#}
