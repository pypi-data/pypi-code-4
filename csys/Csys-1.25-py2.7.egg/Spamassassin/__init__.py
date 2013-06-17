#
__doc__='''Spamassassin processing with MD5 lookups

$Id: setup.py,v 0.01 2007/10/06 00:48:36 csoftmgr Exp $'''

__version__='$Revision: 0.01 $'[11:-2]

import Csys, os, os.path, sys, re

class Config(Csys.CSClass): #{
	_attributes = dict(
		dbhostname	= 'localhost',
		dbtype		= 'postgresql',
		dbname		= None,
		dbusername	= None,
		dbpassword	= None,
		expiretime	= None,
	)
#} Config

configbase = 'spamassassin.conf'

# array of possible configuration files
configFiles = (
	os.path.join(Csys.prefix, 'etc/csadmin', configbase),
	os.path.expanduser(os.path.join('~', '.spamassassin', 'md5sql.conf')),
)
for cfgFile in configFiles: #{
	if os.path.isfile(cfgFile): break
#}
if __name__ == '__main__': #{
	print configFiles
	print cfgFile
#}
