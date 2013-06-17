#!/csoft/bin/python

# $Header: /vol/cscvs/python-Csys/csadmin.py,v 1.4 2005/05/28 04:49:52 csoftmgr Exp $
# $Date: 2005/05/28 04:49:52 $

__doc__='''Celestial Software Admin utilities

$Id: csadmin.py,v 1.4 2005/05/28 04:49:52 csoftmgr Exp $

This program provides an efficient text based tool to handle system
administration tasks on a Linux/Unix bases system running the OpenPKG
package manager.
'''

__version__='$Revision: 1.4 $'[11:-2]

import os, os.path, sys, re

from optparse import OptionParser

verbose = ''

dirname, progname = os.path.split(sys.argv[0])

usage = '''%s: [options] arg1 arg2''' % progname

def run (cmd): #{
	'''Run system command with verbose tracing'''
	if verbose :
		sys.stderr.writelines('run(%s)\n' % cmd)
	return(os.system(cmd))
#}
parser = OptionParser(usage=usage)

parser.add_option('-v', '--verbose',
	action="store_true", dest="verbose", default=False,
	help="verbose output to stderr")

parser.add_option('-e', '--environ',
	action="append", type="string", dest="environ",
	help="ENVIRON ::= VAR=VALUE")

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'

if options.environ: #{
	regexp = re.compile(r"(?P<var>\S+)=(?P<val>.*)")
	for environ in options.environ : #{
		result = regexp.search(environ)
		var = result.group('var')
		if result: #{
			os.environ[var] = result.group('val')
		#}
	#}
#}

import Csys.SysUtils
from Csys.SysUtils import l_prefix
from Csys.Dates import *
from Csys.Curses import *
import Csys.OPKG as opkg
from ConfigParser import ConfigParser

import psycopg

def initialSetup(): #{
	'''Initial System Setup'''
	dbname = 'csadmin'
	config = ConfigParser()
	config.read(os.path.join(sys.prefix, 'etc/csbase/csadmin.conf'))
	cfg = dict(config.items('pgcsadmin'))
	host, user, pw, dbname = (
		cfg['hostname'], cfg['user'], cfg['password'], cfg['database'])
	dsn = 'host=%s dbname=csadmin user=%s password=%s' % (
		host, user, pw)
	print dsn
	if host: dsn += 'host=' + host
	dbh = psycopg.connect(
		host = host,
		database = dbname,
		user = user,
		password = pw,
	)
	print dbh
	dbh.close()
#}

# Main menu structure.
menuTable = {
	'admin': Menu('Celestial Admin Utilities', (
		MenuLine('Initial System Setup', seq=0, action=initialSetup),
		MenuLine('OpenPKG Run Control', action=opkg.runcontrol),
	)),
}
for key in menuTable.keys(): menuTable[key].menuname = key

menuname = 'admin'

# This sets the main title with the current program name.  It
# will later be changed to reflect the active menu.
windows_header_set('Celestial Software Admin', progname)
windows_refresh(redraw=True)

menu = menuTable[menuname]

currentTitle = ''

while True: #{
	rc = menu.getSelection()

	if isinstance(rc, Menu): menu = rc
	elif isinstance(rc, MenuLine): #{
		if rc.action: rc.action()
		else: print rc.prompt
	#}
	elif rc == 'quit': break
	# this should ask for a password since it might be run with sudo
	elif rc == 'sh': #{
		setcook()
		run('/bin/ksh')
		setraw()
	#}
	else: print rc
#} main loop
cursesExit()
