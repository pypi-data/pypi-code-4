#!/usr/local/bin/python

__doc__='''OpenPKG Utilities

$Id: OPKG.py,v 1.4 2005/05/28 04:47:35 csoftmgr Exp $'''

__version__='$Revision: 1.4 $'[11:-2]

import os, sys, re, glob
import curses
from Csys.Curses import *
import signal

from Csys.SysUtils import l_prefix, which

# Prefix to get run control files
_rcPrefix = os.path.join(l_prefix, 'etc', 'rc.d') + '/rc.'

_rc_conf = os.path.join(l_prefix, 'etc', 'rc.conf')

_shtool = which('shtool')

_rc = os.path.join(l_prefix, 'etc', 'rc')

def packagesInstalled(): #{
	'''List of packages installed'''
	packages = map(lambda s: s.replace(_rcPrefix, ''), 
		glob.glob('%s*' % _rcPrefix))
	packages.sort()
	return packages
#}

_rcVals = { # values of package variables
	'yes':		True,
	'unknown':	None,
	'no':		False,
}

class runControl: #{
	'''OpenPKG run control'''
	def __init__(self, pkgname): #{
		'''Set base attributes'''
		d = self.__dict__
		d['nameOriginal']	= pkgname
		d['name']			= pkgname.replace('-', '_')
		d['enable']			= True
		d['usable']			= None
		d['active']			= True
	#} __init__

	def __str__(self): return self.name

	def __setattr__(self, attrname, val): #{
		'''Set Attribute'''
		d = self.__dict__

		if attrname in ('enable', 'usable', 'active'):
			try:	d[attrname] = _rcVals[val.lower()]
			except KeyError: d[attrname] = None
		else:
			d[attrname] = val

		return(d[attrname])
	#} __setattr__

	def packageEnable(self): #{
		'''Enable Package (remove pkgname_enable) from rc.conf'''
		if not self.enable: #{
			cmd = r'''%s subst -e '/\b%s_enable\b/d' %s''' % (
				_shtool, self.name, _rc_conf)
			os.system(cmd)
			cmd = r'''%s %s start 2>/dev/null''' % ( _rc, self.name )
			os.system(cmd)
			self.rcStart() # start it up.
		#}
		self.__dict__['enable'] = True # hopefully
	#} packageEnable

	def packageDisable(self): #{
		'''Enable Package (remove pkgname_enable) from rc.conf'''
		if self.enable: #{
			self.rcStop() # make sure it's not running
			cmd = r'''%s %s stop 2>/dev/null''' % ( _rc, self.name )
			os.system(cmd)
			cmd = r'''%s subst -e '/\b%s_enable\b/d' %s 2>/dev/null''' % (
				_shtool, self.name, _rc_conf)
			os.system(cmd)
			cmd = r'''%s subst -e '$s/$/\n\t%s_enable="no"/' %s''' % (
				_shtool, self.name, _rc_conf)
			os.system(cmd)
		#}
		self.__dict__['enable'] = False
	#} packageDisable

	def rcStart(self): #{
		'''Start Package'''
		if self.enable: #{
			cmd = '''%s %s start 2>/dev/null''' % ( _rc, self.nameOriginal )
			os.system(cmd)
		#}
	#} rcStart

	def rcStop(self): #{
		'''Stop Package'''
		if self.enable: #{
			cmd = '''%s %s stop 2>/dev/null''' % ( _rc, self.nameOriginal )
			os.system(cmd)
		#}
	#} rcStop

	def rcRestart(self): #{
		'''Restart Package'''
		if self.enable: #{
			cmd = '''%s %s restart 2>/dev/null''' % ( _rc, self.nameOriginal )
			os.system(cmd)
		#}
	#} rcRestart

	def rcReload(self): #{
		'''Reload Package'''
		if self.enable: #{
			cmd = '''%s %s reload 2>/dev/null''' % ( _rc, self.nameOriginal )
			os.system(cmd)
		#}
	#} rcReload

	def Status(self): #{
		'''Get Status from run control'''
		return(packageStatus(pkgname=self.name))
	#} Status

#} class runControl

# regular expressions to scan ``rc xxx status'' output
_reEnable = re.compile(r'(.*)_enable=.(.*).$')
_reUsable = re.compile(r'(.*)_usable=.(.*).$')
_reActive = re.compile(r'(.*)_active=.(.*).$')

_packagesInstalled = {}

def _loadPackagesInstalled(force): #{
	'''Load _packagesInstalled dictionary'''
	global _packagesInstalled
	if force or not _packagesInstalled: #{
		if force: _packagesInstalled = []
		packages = packagesInstalled()
		for package in packages: #{
			p = _packagesInstalled[package] = runControl(package)
			_packagesInstalled[p.name] = p
		#}
	#}
	try: _packagesInstalled.pop('openpkg')
	except: pass
	return _packagesInstalled
#} _loadPackagesInstalled

def packageStatus(force=False, pkgname='all'): #{
	'''Build Run Control Display'''
	_packagesInstalled = _loadPackagesInstalled(force)
	fh = os.popen('%s %s status 2>/dev/null' % (_rc, pkgname))
	for line in fh.readlines(): #{
		# print line
		try: #{ # may fail when attempting to update ''openpkg''
			re = _reEnable.match(line)
			if re : #{
				# print '%s %s' % ( re.group(1), re.group(2) )
				package, val = _packagesInstalled[re.group(1)], re.group(2)
				package.enable = val
				continue
			#}
			re = _reUsable.match(line)
			if re : #{
				package, val = _packagesInstalled[re.group(1)], re.group(2)
				package.usable = val
				continue
			#}
			re = _reActive.match(line)
			if re : #{
				package, val = _packagesInstalled[re.group(1)], re.group(2)
				package.active = val
				continue
			#}
		#}
		except: pass
	#}
	fh.close()
	return _packagesInstalled
#} packageStatus

def pkgKeys(): #{
	'''Return list of original package keys (no ``-'' replacement)'''
	keydict = dict(
		map(lambda k: ( _packagesInstalled[k].nameOriginal, 1 ),
			_packagesInstalled.keys())
	)
	keys = keydict.keys()
	keys.sort()
	return keys
#} pkgKeys

# output of ``rc --config'' command
_reConfig = re.compile(r'^(.*)_([^_\s]*)\s+"(.*)"\s+([=!]=)\s+"(.*)"$')

def packageConfig(force=False): #{
	'''Get Package enabled status from rc --config command'''
	_packagesInstalled = _loadPackagesInstalled(force)
	fh = os.popen('%s/etc/rc --config status 2>/dev/null' % l_prefix)
	for line in fh.readlines(): #{
		re = _reConfig.search(line.rstrip())
		if re: #{
			(name, action, val1, flag, val2) = re.groups()
			try:
				package = _packagesInstalled[name]
				package.__setattr__(action, val1)
				package.__setattr__('flag', flag)
			except KeyError: continue
		#}
	#}
	fh.close()
	return _packagesInstalled
#} packageConfig

# Names for the run control columns
# Looping through this list makes it easy to address the columns
rcNames = ('active', 'inactive', 'disabled')

# named variables for clarity
column_active, column_inactive, column_disabled = range(3)

rcMenuLines		= {} # table of menuLines for each column
rcMenus			= {} # The ScrollMenu for each column
rcwin			= '' # The main Curses window for the runcontrol
rcWindows		= {} # The rcwin derived windows for each column

# dictionary of userPrompts for each column
rcPrompts = {
	'active': (
		UserPrompt('s', '[S]top'),
		UserPrompt('r', '[R]estart'),
		UserPrompt('l', 're[L]oad'),
		UserPrompt('d', '[D]isable'),
		UserPrompt('a', '[A]larm'),
	),
	'inactive': (
		UserPrompt('s', '[S]tart'),
		UserPrompt('d', '[D]isable'),
		UserPrompt('a', '[A]larm'),
	),
	'disabled': (
		UserPrompt('e', '[E]nable'),
		UserPrompt('a', '[A]larm'),
	),
} #rcPrompts

_alarmTime = 0

_newTables = False

def _handleAlarm(signum, frame): #{
	'''Alarm Handler'''
	# reset signal
	signal.alarm(0)	# set to zero

	# reset the signal for those systems that turn it off when caught
	signal.signal(signal.SIGALRM, _handleAlarm)

	_rcBuildTables() # rebuild tables
#} _handleAlarm

def setAlarm(): #{
	'''Prompt and set alarm time to seconds (0) is off'''

	global _alarmTime

	while True: #{
		s = prompt_getstr('Set Alarm Seconds (30 second minimum, 0 is off)')
		if not s: return
		try: seconds = int(s)
		except: #{
			unerrs('Invalid input >%s< % s')
			continue
		#}
		if seconds < 0: #{
			unerrs('Negative time not allowed')
			continue
		#}
		if seconds > 0: seconds = max(30, seconds)
		_alarmTime = seconds
		break
	#}
	leftTitle = ''
	if seconds: leftTitle = 'Alarm %s seconds' % seconds
	windows_title_set(currentTitle, left=leftTitle, refresh=True)
#} setAlarm

def _rcBuildTables(pkgname='all'): #{
	'''Build Run Control Columns'''

	# subentry('_rcBuildTables')

	global rcMenuLines
	global rcMenus
	global rcWindows
	global rcwin
	global _newTables

	_newTables = True # tell the world the tables are true

	# empty arrays
	pkgtables = {}
	for name in rcNames: #{
		table = rcMenuLines[name]
		while table: table.pop()
		pkgtables[name] = []
	#}
	dsp_prmpt('getting package status info...')
	packages = packageStatus(pkgname=pkgname)
	dsp_prmpt('')

	keys = pkgKeys() # get sorted original keys
	# put the packages in the proper bin
	for key in keys: #{
		pkg = packages[key]
		if not pkg.enable:	colname = 'disabled'
		elif pkg.active:	colname = 'active'
		else:				colname = 'inactive'
		pkgtables[colname].append(pkg)
	#}
	# now put them in the approprate MenuLines
	for name in rcNames: #{
		menuLines = rcMenuLines[name]
		seq = 0
		for pkg in pkgtables[name]: #{
			menuLines.append(MenuLine(pkg.name, seq, data=pkg))
			seq += 1
		#}
	#}
	# now create the MenuScroll objects
	for name in rcNames: rcMenus[name].reload()
	
	# enable signal interface
	signal.signal(signal.SIGALRM, _handleAlarm)

#} _rcBuildTables

def runcontrol(): #{
	'''Build Run Control Display'''

	# subentry('runcontrol')

	global rcMenuLines
	global rcMenus
	global rcWindows
	global rcwin
	global _newTables
	global currentTitle

	signal.alarm(0) # turn off alarm

	currentTitle = 'OpenPKG Run Control'
	windows_title_set(currentTitle, refresh=True)

	if not rcwin: #{ initialize the first time
		# Create a window using all display space
		rcwin = curses.newwin(term_lines_avail, term_co, term_firsty, 0)
		max_y, max_x = rcwin.getmaxyx()
		offset = 0
		colwidth = int(max_x / 3)
		for name in rcNames: #{
			win = rcWindows[name] = rcwin.derwin(max_y, colwidth, 0, offset)
			offset += colwidth
			menuLines = rcMenuLines[name] = []
			rcMenus[name] = MenuScroll('', menuLines, hdrLine = name,
				border = True, win = win, vcenter = False,
				userPrompts=rcPrompts[name]
			)
		#}
	#}
	else: #{
		try: windows_body.remove(rcwin)
		except ValueError: pass
	#}
	windows_body.append(rcwin)
	rcwin.noutrefresh()
	windows_refresh(redraw=True)

	# create tuple of menus.
	menus = tuple(map(lambda name: rcMenus[name], rcNames))
	n = len(menus) - 1

	column = 0
	column_motion = 0

	pkgname = 'all' # select all packages the first time
	while True: #{
		if pkgname: _rcBuildTables(pkgname=pkgname)
		pkgname = None
		column += column_motion
		# this causes the active window to wrap
		if   column < 0: column = n
		elif column > n: column = 0

		menu = menus[column]
		if menu.noEntries <= 0: #{ # skip empty columns
			if column_motion == 0: column_motion = 1
			continue
		#}
		column_motion = 0

		_newTables = False
		signal.alarm(_alarmTime)

		try: rc = menu.getSelection()
		except: continue # probably alarm went off

		signal.alarm(0)

		line = menu.curmenu
		pkg = line.data
		if isinstance(rc, MenuLine): continue
		if   rc == 'q' or rc == EXIT_NOW: break
		if   rc == KEY_TAB:  column_motion = 1
		elif rc == KEY_BTAB: column_motion = -1
		elif rc == 'a': setAlarm()
		elif column < column_disabled: #{ enabled, but perhaps not active
			pkgname = pkg.nameOriginal
			if rc == 'd': #{
				if yorn('Disable %s' % pkgname):                 pkg.packageDisable()
				continue
			#}
			if column == column_active: #{
				if   rc == 's' and yorn('Stop %s' % pkgname):    pkg.rcStop()
				elif rc == 'r' and yorn('Restart %s' % pkgname): pkg.rcRestart()
				elif rc == 'l' and yorn('Reload %s' % pkgname):  pkg.rcReload()
				else: pkgname = None
			#}
			elif column == column_inactive: #{
				if rc == 's' and yorn('Start %s' % pkgname):     pkg.rcStart()
				else: pkgname = None
			#}
		#}
		elif column == column_disabled: #{
			pkgname = pkg.nameOriginal
			if rc == 'e' and yorn('Enable %s' % pkgname):        pkg.packageEnable()
			else: pkgname = None
		#}
		else: #{
			print 'invalid >%s<' % rc
			curses.beep()
		#}
	#}
	try: windows_body.remove(rcwin)
	except ValueError: pass
	signal.alarm(0) # turn off alarm
#} runcontrol

if __name__ == '__main__': #{
	packages = packageConfig()
	uniq = dict(map(lambda p: (p, 1),
		map(lambda p: packages[p].nameOriginal, packages.keys())))
	keys = uniq.keys()
	keys.sort()
	csbase = packages['csbase']
	print csbase.enable
	csbase.packageDisable()
	print csbase.enable
	csbase.packageEnable()
	print csbase.enable
	#for key in keys: #{
	#	package = packages[key]
	#	print key, package.enable
	##}
#}
