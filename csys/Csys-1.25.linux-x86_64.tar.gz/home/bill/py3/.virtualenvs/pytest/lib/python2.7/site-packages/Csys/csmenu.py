#!/csoft/bin/python

# $Header: /vol/cscvs/python-Csys/csmenu.py,v 1.5 2011/10/05 23:02:55 csoftmgr Exp $
# $Date: 2011/10/05 23:02:55 $

__doc__='''Celestial Software Admin utilities

$Id: csmenu.py,v 1.5 2011/10/05 23:02:55 csoftmgr Exp $

csmenu provides a quick-n-dirty menu given any directory at its only
argument.  It will find all executable programs under that menu, and
display a scrolling area for selection.
'''

__version__='$Revision: 1.5 $'[11:-2]

import os, os.path, sys, re, stat, Csys
import signal

from optparse import OptionParser

verbose, suffix = ('', os.getpid())

dirname, progname = os.path.split(sys.argv[0])

usage = '''%s: [options] arg1 arg2''' % progname

def run (cmd): #{
	'''Run system command with verbose tracing'''
	if verbose :
		sys.stderr.writelines('run(%s)\n' % cmd)
	return(Csys.system(cmd))
#}
parser = OptionParser(usage=usage)

parser.add_option('-v', '--verbose',
	action="store_true", dest="verbose", default=False,
	help="verbose output to stderr")

parser.add_option('-r', '--rmopkgenv',
	action="store_true", dest="rmopkgenv", default=False,
	help="Remove %s from enviornment" % Csys.prefix)

parser.add_option('-e', '--environ',
	action="append", type="string", dest="environ",
	help="ENVIRON ::= VAR=VALUE")

(options, args) = parser.parse_args()

if options.verbose: #{
	verbose = '-v'
	suffix = ''
#}
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
if options.rmopkgenv: #{
	import Csys.rmopkgenv
	Csys.rmopkgenv.rmopkgenv()
#}
stty = os.path.join(Csys.prefix, 'bin/stty')
Csys.run("%s erase '^h'" % stty, verbose)

if not args: args.append('~/lbin')

import Csys.SysUtils
from Csys.SysUtils import l_prefix
from Csys.Dates import *
from Csys.Curses import *

dir = os.path.expanduser(args[0])

class Program(object): #{
	def __init__(self, prompt, prog): #{
		'''Create menu Line compatible object'''
		self.prompt = prompt
		self.prog	= prog
	#}
	def __str__(self): return(self.prompt)

	def __cmp__(self, other): return(cmp(self.prog, other.prog))
#}
menuLines = []

skipPatterns = (
	re.compile(r'^\.'),
	re.compile(r'^tmp', re.IGNORECASE),
	re.compile(r'\.gz$'),
	re.compile(r'\.Z$'),
)
def dumpwalk(arg, dname, fnames): #{
	arg = re.sub(r'/*$', '/', arg) # add single trailing '/'
	for fname in fnames: #{ # loop through the names in the directory
		for pat in skipPatterns: #{
			if pat.search(fname): #{
				fname = None
				break
			#}
		#}
		if fname is None: continue
		p = os.path.join(dname, fname)
		if not os.access(p, os.X_OK): continue
		if os.path.isdir(p): #{
			if os.path.islink(p): #{
				r = os.path.realpath(p)
				os.path.walk(r, dumpwalk, os.path.dirname(r))
			#}
			continue
		#}
		prompt = p.replace(arg, '')
		line = Program(prompt, p)
		menuLines.append(line)
	#}
#}
os.path.walk(dir, dumpwalk, dir)
menuLines.sort()
seq = 0
for i in range(len(menuLines)): #{
	line = menuLines[i]
	menuLines[i] = MenuLine(line.prompt, seq=seq, action=line)
	seq += 1
#}
# print "\n".join(menuLines)

# Main menu structure.
menuTable = {
	'main': MenuScroll(dir, menuLines, border = True, win = win_body,),
}
for key in menuTable.keys(): menuTable[key].menuname = key

menuname = 'main'

# This sets the main title with the current program name.  It
# will later be changed to reflect the active menu.
windows_header_set('Program Selection', progname)
windows_refresh(redraw=True)

menu = menuTable[menuname]
menu.enterok = True

currentTitle = ''

while True: #{
	rc = menu.getSelection()
	if not isinstance(rc, MenuLine): #{
		curses.beep()
		if yorn('Quit?'): #{
			break
		#}
		continue
	#}
	setcook()
	run(rc.action.prog)
	setraw()
#}
cursesExit()
