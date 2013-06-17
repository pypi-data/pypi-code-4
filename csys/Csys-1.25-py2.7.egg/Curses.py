#!/usr/local/bin/python

__doc__='''Curses Screen utilities

$Id: Curses.py,v 1.15 2013/06/11 19:50:23 csoftmgr Exp $'''

__version__='$Revision: 1.15 $'[11:-2]

import curses, sys, re, os
import curses.ascii as ascii
import time
import termios
import copy
import Csys

# This will be set the first time curses is invoked
os.environ['CsysCurses'] = 'True'

savetty = None
ttyfd	= None

if savetty is None: #{
	ttyfd = sys.stdin.fileno()
	savetty = termios.tcgetattr(ttyfd)
#}

# This should be true if called from pydoc -- which can cause
# heartburn with one's terminal environment.

_inPyDoc = os.environ.get('_', '').endswith('/pydoc')

if not _inPyDoc: #{
	stdscr = curses.initscr()
	curses.def_shell_mode()
	curses.noecho()
	curses.raw()
	curses.def_prog_mode()

	term_li, term_co	= stdscr.getmaxyx()
	term_firsty			= 2
	term_lasty			= term_li - 1
	term_lines_avail	= term_lasty - term_firsty - 1
	max_fields			= term_li * term_co # one field per position
	win_header			= curses.newwin(1, term_co, 0, 0)
	win_title			= curses.newwin(1, term_co, 1, 0)
	win_body			= curses.newwin(term_lines_avail, term_co, term_firsty, 0)
	win_print			= curses.newwin(5, term_co, term_lasty - 6, 0)
	win_command			= curses.newwin(1, term_co, term_lasty - 1, 0)
	win_status			= curses.newwin(1, term_co, term_lasty, 0)
	body_lines			= term_li - 4

	windows_top			= [ win_header, win_title ]
	windows_body		= [ win_body ]
	windows_bottom		= [ win_command, win_status ]
#}

def windows_body_remove(win): #{
	'''Remove window from body array'''
	try: windows_body.remove(win)
	except ValueError: pass
#} windows_body_remove

class winPrint(object): #{
	'''Redirect print statements to Window'''
	def write(self, str): #{
		# str = str.strip('\n')
		win_print.clear()
		win_print.border()
		win_print.move(1, 1)
		win_print.addstr(str, curses.A_BOLD)
		win_print.refresh()
		win_print.getch()
		windows_refresh(redraw=True)
	#}
#} class winPrint

if not _inPyDoc: sys.stdout = winPrint()

def windows_refresh(redraw=False): #{
	'''Refresh all current windows and do update'''
	if redraw: #{
		stdscr.clear()
		stdscr.noutrefresh()
	#}
	for win in windows_top + windows_body + windows_bottom: #{
		if redraw: win.touchwin()
		win.noutrefresh()
	#}
	curses.doupdate()
#} windows_refresh

_headerTitle = ''

def windows_header_set(title=None, scrname=None, refresh=False): #{
	'''Set header'''
	global _headerTitle
	win_max_y, win_max_x = win_header.getmaxyx()
	win_header.clear()
	if scrname: #{
		win_header.move(0, 0)
		win_header.addstr('[%s]' % scrname)
	#}
	if title: _headerTitle = title
	title = _headerTitle
	if title: #{
		win_header.move(0, (win_max_x - len(title))/2)
		win_header.addstr(title)
	#}
	datestr = time.strftime('%m/%d/%y %H:%M', time.localtime())
	x = win_max_x - len(datestr) - 1
	win_header.move(0, x)
	win_header.addstr(datestr)
	if refresh: win_header.refresh()
#} windows_header_set

def windows_title_set(title, left=None, right=None, refresh=False): #{
	'''Set title'''
	win_max_y, win_max_x = win_title.getmaxyx()
	win_title.clear()
	if left: #{
		win_title.move(0, 0)
		win_title.addstr('[%s]' % left)
	#}
	if title: #{
		win_title.move(0, (win_max_x - len(title))/2)
		win_title.addstr(title)
	#}
	if right: #{
		x = win_max_x - len(right) - 1
		win_title.move(0, x)
		win_title.addstr(right)
	#}
	if refresh: win_title.noutrefresh()
#} windows_title_set

SUCCEED			= 0
FAIL			= -1

first			= 1
next			= 2
only			= 3
prev			= 4
last			= 5
SHRTFLD			= 1
LONGFLD			= 2
DBLFLD			= 3
INVFLD			= -1
PRMPTLINE		= 21
EOF				= (-1)
UPKEY			= (-2)
ENTER			= (-3)
SEARCH			= (-5)
SAVE			= (-6)
UP_ARROW		= UPKEY
DOWN_ARROW		= (-7)
LEFT_ARROW		= (-8)
RIGHT_ARROW		= (-9)
CLEAR_TO_END	= (-10)
INSERT_CHAR		= (-11)
DELETE_CHAR		= (-12)
HOME_KEY		= (-13)
BACKSPACE		= (-14)
RECALL			= (-15)
END_OF_FIELD	= (-16)
CLEAR_FIELD		= (-17)
HELP			= (-19)
SYSTEM			= (-20)
EXIT_NOW		= (-21)
KEY_REDRAW		= (-22)
CASE_CHANGE		= (-23)
KEY_PREV		= (-24)
KEY_PGUP		= (-25)
KEY_PGDOWN		= (-26)
KEY_END			= (-27)
KEY_TAB			= (-28)
KEY_BTAB		= (-29)
KEY_CANCEL		= (-30)
INVALID_FUNC	= (-999)
NEXT_FIELD		= 1
SAME_FIELD		= 0
PREV_FIELD		= -1
NO_NEXT_FIELD	= (-1)
# make these the same to avoid conflicts.
RTRNNORM		= SAME_FIELD
RTRNPREV		= PREV_FIELD
RTRNNEXT		= NEXT_FIELD

# Exceptions
ResultFAIL		= 'FAIL'

KeyBACKSPACE	= str(BACKSPACE)
KeyCLEAR_FIELD	= str(CLEAR_FIELD)
KeyCLEAR_TO_END	= str(CLEAR_TO_END)
KeyDELETE_CHAR	= str(DELETE_CHAR)
KeyDOWN_ARROW	= str(DOWN_ARROW)
KeyEND_OF_FIELD	= str(END_OF_FIELD)
KeyENTER		= str(ENTER)
KeyEOF			= str(EOF)
KeyEXIT_NOW		= str(EXIT_NOW)
KeyHOME			= str(HOME_KEY)
KeyINSERT_CHAR	= str(INSERT_CHAR)
KeyREDRAW		= str(KEY_REDRAW)
KeyLEFT_ARROW	= str(LEFT_ARROW)
KeyRECALL		= str(RECALL)
KeyRIGHT_ARROW	= str(RIGHT_ARROW)
KeySAVE			= str(SAVE)
KeySEARCH		= str(SEARCH)
KeyUPKEY		= str(UPKEY)
KeyCASE_CHANGE	= str(CASE_CHANGE)
KeyPREV			= str(KEY_PREV)
KeyPGUP			= str(KEY_PGUP)
KeyPGDOWN		= str(KEY_PGDOWN)
KeyEND			= str(KEY_END)
KeyTAB			= str(KEY_TAB)
KeyBTAB			= str(KEY_BTAB)
KeyCANCEL		= str(KEY_CANCEL)

class Error(Exception): #{
	'''Base class for Csys.Curses exceptions'''
	def __init__(self, msg=''): #{
		self.message = msg
		Exception.__init__(self, msg)
	#} __init__

	def __str__(self): return self.message

	def __repr__(self): return 'Error(%s)' % self.message

#} class Error

_keyExceptionMap = {
	ascii.DLE			: KeyPREV,		# ctrl-p
	curses.KEY_UP		: KeyUPKEY,
	ascii.NAK			: KeyUPKEY,		# ctrl-U
	ascii.LF			: KeyENTER,		# ctrl-j
	curses.KEY_ENTER	: KeyENTER,
	curses.KEY_LEFT		: KeyLEFT_ARROW,
	ascii.BS			: KeyBACKSPACE,	# ctrl-h
	curses.KEY_BACKSPACE: KeyBACKSPACE,
	curses.KEY_RIGHT	: KeyRIGHT_ARROW,
	curses.KEY_DOWN		: KeyDOWN_ARROW,
	curses.KEY_F1		: KeyINSERT_CHAR,
	curses.KEY_IC		: KeyINSERT_CHAR,
	ascii.HT			: KeyINSERT_CHAR,	# ctrl-i
	curses.KEY_F2		: KeyDELETE_CHAR,
	curses.KEY_DC		: KeyDELETE_CHAR,
	ascii.EOT			: KeyDELETE_CHAR,	# ctrl-d
	curses.KEY_F3		: KeyCLEAR_TO_END,
	ascii.SI			: KeyCLEAR_TO_END,	# ctrl-o
	ascii.ENQ			: KeyEND_OF_FIELD,	# ctrl-e
	curses.KEY_END		: KeyEND_OF_FIELD,
	curses.KEY_F4		: KeySAVE,
	curses.KEY_NPAGE	: KeySAVE,
	curses.KEY_PPAGE	: KeyPGUP,
	curses.KEY_F5		: KeySEARCH,
	curses.KEY_F6		: KeyRECALL,
	ascii.DC2			: KeyRECALL,		# ctrl-r
	ascii.CAN			: KeyEXIT_NOW,		# ctrl-x
	ascii.SUB			: KeyCLEAR_FIELD,	# ctrl-z
	ascii.FF			: KeyREDRAW,		# ctrl-l
	curses.KEY_HOME		: KeyHOME,
	ord('~')			: KeyCASE_CHANGE,	# tilda
	ascii.ETX			: KeyCANCEL,		# ctrl-c
} # _keyExceptionMap

def wgetchar(win, map=_keyExceptionMap): #{
	'''Get next character from window raising exceptions for function keys'''
	win.keypad(1)
	while True: #{
		win.refresh() # it's nice to see what we're doing.
		c = win.getch()
		exc = map.get(c, None)
		if exc: raise exc
		if curses.ascii.isprint(c): return(c)
		curses.beep()
		unerrs('invalid response %s' % curses.keyname(c))
	#}
#} wgetchar

if not _inPyDoc: #{{
	# Global attributes and variables
	# dsp_prmpt			= ''
	cur_attribute		= None
	need_to_initialize	= False
	cur_x				= 0
	cur_y				= 0
	a_blink				= curses.A_BLINK
	a_bold				= curses.A_BOLD
	a_clear				= stdscr.clear
	a_clear_prot		= None
	a_clrtobot			= stdscr.clrtobot
	a_clrtoeol			= stdscr.clrtoeol
	a_dim				= curses.A_DIM
	a_exit_attr			= stdscr.attroff
	a_exit_so			= curses.A_NORMAL
	a_full				= curses.A_NORMAL
	a_normal			= curses.A_NORMAL
	a_off_prot			= None
	a_on_prot			= None
	a_reverse			= curses.A_REVERSE
	a_exit_rev			= curses.A_NORMAL
	a_standout			= curses.A_STANDOUT
	_refresh_all		= True
	errbug				= ''
	_curscr				= stdscr
	_savscr				= None
	verbose				= False
	use_comma			= False

	curscr = None
#}
else: #{
	a_standout			= None
	term_firsty			= None
	term_co				= None
	body_lines			= None
	term_lines_avail	= None
#}}

class instringBuffer(object): #{
	'''Simple Class with .str attribute'''
	def __init__(self, str=''): #{
		self.str = str
	#} __init__

	def __str__(self): return self.str

#} instringBuffer

# Utility routines
def instring(win, x, y, ubuf, displen, numeric=False, ext_results=True,
	i=0,
	attr=a_standout,
): #{
	'''Get input from terminal

	The return is an integer indicating the type of key press, and the
	attribute, ubuf.str will be set.
	'''

	try: passwd = ubuf.fdesc.passwd
	except AttributeError: passwd = False

	def win_addstr(y, x, buf, attr): #{
		'''Display string or '*' fill on passwords'''

		if passwd: s = '*' * len(buf)
		else: s = buf

		win.move(y, x)
		win.addstr(s, attr)
	#} win_addstr

	rc = SUCCEED
	if not win: #{
		unerrs('instring: no window defined')
		return None
	#}
	global save_requested
	save_requested = False
	max_y, max_x = win.getmaxyx()
	# strip leading an trailing white space
	buf = str(ubuf).strip()
	# last_char is one greater than the highest index in buf
	last_char = len(buf)
	# This will create strings with trailing whitespace to fill
	# the display field
	displen = min(max_x - x - 1, displen)
	fmt = '%%-%ds' % displen
	buf = fmt % buf
	try: #{{
		win_addstr(y, x, buf, attr)
	#}
	except: #{
		unerrs('instring: y = %d x = %d len %d' % (y, x, len(buf)))
		unerrs('instring: x = %d max_x - x = %d, displen = %d' % (
			x, (max_x - x), displen))
		unerrs('instring buf >%s<' % buf)
	#}}

	done = False
	# i = 0
	win.keypad(1)
	while i < displen and not done: #{
		cur_x = x + i
		win.move(y, cur_x)
		last_i = last_char - 1
		# If we try to go beyond the end of the field, drop down
		# to the command window to get the data.
		if cur_x >= max_x: #{
			rc = instring(win_command, 0, 0, ubuf, displen, ext_results)
			win_command.clear()
			return(rc)
		#}
		win.refresh() # we need to see it to enter data.
		try: #{{
			c = wgetchar(win)
			# translate function keys and synonyms
		#}
		except KeyCANCEL: #{
			done = True
			rc = KEY_CANCEL
			break
		#}
		except KeySAVE: #{
			save_requested = done = True
			rc = SAVE
			break
		#}
		except KeyUPKEY: #{
			rc = UPKEY
			break
		#}
		except KeyCLEAR_FIELD: #{
			buf = ' ' * displen
			i = last_char = 0
			win_addstr(y, x, buf, attr)
		#}
		except KeyCLEAR_TO_END: #{
			rbuf = ' ' * (last_char - i)
			win_addstr(y, cur_x, rbuf, attr)
			buf = buf[:i] + rbuf
			done = (i > 0)
		#}
		except KeyPREV: #{ ctrl-p
			rc = KEY_PREV
			break
		#}
		except KeyDOWN_ARROW: #{
			rc = DOWN_ARROW
			break
		#}
		except KeyHOME: #{
			rc = HOME_KEY
			break
		#}
		except (KeyEOF, KeyENTER): #{
			rc = ENTER
			break
		#}
		except (KeyBACKSPACE, KeyLEFT_ARROW): #{
			i = max(0, i - 1)
		#}
		except KeyEND_OF_FIELD: #{
			i = last_char
		#}
		except KeyRIGHT_ARROW: #{
			i = min(i + 1, last_char - 1)
		#}
		except KeyINSERT_CHAR: #{
			rbuf = ' ' + buf[i:last_char] # new right side
			# this test sequence will either increment the
			# last_char pointer if there's room in the field or
			# strip off the last character of rbuf which would be
			# too long to fit.
			if last_char < displen: #{{
				last_char += 1
			#}
			else: #{
				rbuf = rbuf[:-1]
			#}}
			win_addstr(y, cur_x, rbuf, attr)
			buf = buf[:i] + rbuf
		#}
		except KeyDELETE_CHAR: #{
			# This will shift the string left one and append a space
			rbuf = buf[i+1:] + ' '
			win_addstr(y, cur_x, rbuf, attr)
			buf = buf[:i] + rbuf
			last_char = min(0, last_char - 1)
		#}
		except KeyCASE_CHANGE: #{
			dsp_prmpt('change case i = %d' % i)
			s = rbuf = buf[i] # character under the cursor
			d = ord(s) # int suitable for ascii tests
			if ascii.islower(d):	rbuf = rbuf.upper()
			elif ascii.isupper(d):	rbuf = rbuf.lower()
			if s != rbuf: #{
				win_addstr(y, cur_x, rbuf, attr)
				buf = buf[:i] + rbuf + buf[i+1:]
			#}
			i += 1
		#}
		except KeyEXIT_NOW: #{
			rc = EXIT_NOW
			if not ext_results: rc = UPKEY
			break
		#}
		except KeyRECALL: #{
			rc = RECALL
			if not ext_results: rc = UPKEY
			break
		#}
		except KeyREDRAW: #{
			windows_refresh(redraw = True)
			continue
		#}
		else: #{
			if not ascii.isascii(c): #{
				dsp_prmpt('invalid response %s' % curses.keyname(c))
				curses.beep()
				continue
			#}
			c = chr(c)
			win_addstr(y, cur_x, c, attr)
			rbuf = c + buf[i+1:displen]
			buf = buf[:i] + rbuf
			i += 1
			if ( i >= last_char ): last_char = i + 1
		#}}
	#}
	win.keypad(1)
	buf = buf.strip()
	if rc == ENTER and buf:			rc = SUCCEED
	elif rc == SUCCEED and not buf:	rc = ENTER
	win_addstr(y, x, fmt % buf, curses.A_BOLD)
	ubuf.str = buf
	win.refresh()
	return(rc)
#} instring

PRN_ON				= False # set True to enable pass-through printing
PRN_OFF				= False
term_prn_on			= False
rm_prn_on			= False

def prnctrl(flag=False): #{
	'''Turn pass through printing on/off depending on flag'''
	if PRN_ON: #{{
		if flag: curses.putp('prtr_on')
		else	: curses.putp('prtr_off')
	#}
	else: flag = False #}
	term_prn_on = flag
	return(flag)
#} prnctrl

def addstr(str): #{
	_curscr.addstr(str)
	# _curscr.refresh()
#} addstr

def mvaddstr(y, x, str): #{
	_curscr.move(y, x)
	_curscr.addstr(str)
#} mvaddstr

def unerrs(msg, returnChar=False): #{
	'''Display error message in status line'''
	win = win_command
	win_max_y, win_max_x = win.getmaxyx()
	dsp_x = (win_max_x - len(msg)) / 2
	win.clear()
	win.move(0, dsp_x)
	win.addstr('%s ' % msg)
	c = win.getch()
	if not returnChar: c = FAIL
	return c
#} unerrs

_yorn = {
	ord('y') : True,
	ord('Y') : True,
	ord('n') : False,
	ord('N') : False,
} # _yorn

def yorn(msg): #{
	'''Display Prompt returning True if 'Y' or 'y' returned'''
	c = unerrs('%s (y/n)' % msg, True)
	return(_yorn.get(c, False))
#} yorn

def subentry(subname): #{
	'''Trace Subroutine Calls'''
	if verbose and yorn('Enter %s abort?' % subname): cursesExit()
#} subentry

pre_prompt = None

def dsp_prmpt(msg, getc=False): #{
	'''Display error message in status line

	If getc is true, it will add [ ] to the end of the prompt and return
	return that character.
	'''
	win = win_command
	win_max_y, win_max_x = win.getmaxyx()
	max_lgth = win_max_x - 3
	l = len(msg)
	if(l >= max_lgth): #{
		msg = msg[:max_lgth]
		l = len(msg)
	#}
	if getc: msg = msg + ' [ ]'
	dsp_x = (win_max_x - l) / 2
	win.clear()
	win.move(0, dsp_x)
	win.addstr('%s ' % msg)
	win.refresh()
	if getc: #{
		x = len(msg) - 2
		win.move(0, x)
		c = wgetchar(win)
		win.addch(0, x, c)
		win.refresh()
		return(c)
	#}
#} dsp_prmpt

def prompt_getstr(prompt): #{
	'''Display Prompt and return string'''
	win = win_command
	max_y, max_x = win.getmaxyx()
	max_lgth = max_x - 3

	if prompt.find(':') == -1: prompt = prompt + ':'
	dsp_x = len(prompt) + 1
	win.clear()
	win.move(0, 1)
	win.addstr('%s ' % prompt)
	ubuf = instringBuffer()
	rc = instring(win, dsp_x, 0, ubuf, (max_x - dsp_x), attr=a_normal)
	win.clear()
	win.refresh()
	return ubuf.str
#} dsp_prmpt

DSP_SUBNAME = False

def dsp_subname(name): #{
	'''Debug internal curses screen calls'''
	if not DSP_SUBNAME: return
	win_max_y, win_max_x = win_command.getmaxyx()
	errbuf = '[%s] -- abort (y/n)?' % name
	c = unerrs(errbuf)
	if c == 'Y' or c == 'y': #{
		cursesExit()
		sys.exit(0)
	#}
	win_command.clear()
#} dsp_subname

def attrset(attr): #{
	global cur_attribute
	cur_attribute = attr
	_curscr.attrset(attr)
#} attrset

def attroff(): attrset(a_full)

def attron(): attrset(curses.A_REVERSE)

def getcurscr(): #{
	'''Get current screen'''
	global cur_x, cur_y, verbose
	hold_verbose = verbose
	verbose = False
	if _savescr and _curscr and _savescr.scrname != _curscr.scrname: #{
		_curscr	= _savescr
		cur_x	= _curscr.cur_x
		cur_y	= _curscr.cur_y
		_curscr	= _curscr.screen
		_curscr.move(cur_y, cur_x)
		_curscr.refresh()
	#}
	verbose = hold_verbose
	return(_curscr)
#} getcurscr

def cleancrt(): #{
	dsp_subname('cleancrt')
	_curscr.clear()
	_curscr.refresh()
#} cleancrt

def mv_cur(x, y): #{
	global cur_x, cur_y
	cur_x, cur_y = (x, y)
	_curscr.move(y, x)
#} mv_cur

# Menu selection program

def menusel(menu, dfltchar=None,
	top_x=0, top_y=term_firsty, width=term_co, lines=body_lines):
#{
	'''Display menu and return the selected index

	The menu parameter should be an array of tuples with the
	first element the prompt, and the second a code pointer.
	Each prmpt will be in the format `x) prmpt' where the
	character before the left paren will be used as the prompt
	'''
	menutype = type(menu)
	if not (menutype == type([]) or menutype == type(())): #{
		unerrs('menusel: menu argument must be an array or tuple');
		return None
	#}
	n_choices = len(menu)
	if n_choices <= 0: #{
		unerrs('menusel: menu has no lines')
		return None
	#}
	menu_lines = lines - 1
	columns = int(n_choices / menu_lines)
	if n_choices % menu_lines > 0: columns += 1
	prompt_y = min(menu_lines, n_choices)
	if columns > 2: #{
		unerrs('menusel: too many columns %d, max 2' % columns)
		return None
	#}
	col_width = int(width / columns) - 2 # maximum column width
	win_menu = curses.newwin(lines, width, top_y, top_x)
	windows_body.append(win_menu)

	x = 0
	y = 0
	max_lgth = 0
	for menuitem in menu: #{
		prompt = menuitem[0][:col_width]
		n = len(prompt)
		if n > max_lgth: max_lgth = n
	#}
	if columns == 1: #{{
		x = (width - max_lgth) / 2
	#}
	else: #{
		x = (width - columns*max_lgth) / 2
	#}}
	col_width = min(max_lgth, col_width)
	prompts = []
	promptchars = {
		'q'				: EXIT_NOW,
		ascii.CAN		: EXIT_NOW,
		curses.KEY_F4	: SAVE,
	}
	i = 0
	# the next loop will get the prompt characters
	for menuitem in menu: #{
		prompt = menuitem[0][:col_width].replace('.', ')', 1)
		c = prompt[:1]
		promptchars[c] = menuitem[1]
		if dfltchar is None: dfltchar = c
		prompts.append(prompt[0])
		# see if we need to start a new column
		if y >= menu_lines: #{
			y = 0
			x += col_width + 2
		#}
		win_menu.move(y, x)
		win_menu.addstr(prompt)
		i += 1; y += 1
	#}
	prompt = 'Enter ' + ', '.join(prompts) + \
		', q or <CTRL-X> to Exit[%s]' % dfltchar
	x = (width - len(prompt)) / 2
	win_menu.move(prompt_y, x)
	win_menu.addstr(prompt)

	win_menu.keypad(1)
	while True: #{
		windows_refresh()
		c = win_menu.getch()
		try: #{{
			if ascii.isalnum(c): c = '%c' % c
			c = promptchars[c]
			break
		#}
		except: #{
			curses.beep()
			dsp = c
			if not ascii.isalnum(c): dsp = curses.keyname(c)
			dsp_prmpt('invalid response %s' % dsp)
		#}}
	#}
	win_menu.keypad(1)
	windows_body.pop() # remove from top of windows stack
	windows_refresh(redraw=True)
	return(c)
#} menusel

def setcook(): #{
	'''Set terminal in ``cooked'' mode for interactive use'''
	global need_to_initialize
	if need_to_initialize: return
	curses.reset_shell_mode()
	need_to_initialize = True
	sys.stdout = sys.__stdout__
	termios.tcsetattr(ttyfd, termios.TCSADRAIN, savetty)
#} setcook

def setraw(): #{
	'''Set terminal to ``ray'' mode for curses use'''
	global need_to_initialize
	if not need_to_initialize: return
	curses.reset_prog_mode()
	need_to_initialize = False
	sys.stdout = winPrint()
#} setraw

def cursesExit(): #{
	'''Close out curses

	This sets things back to normal for non-curses access.
	'''
	stdscr.move(term_lasty, 0) # position cursor at bottom of screen
	stdscr.refresh()
	setcook()
	sys.stdout = sys.__stdout__
	os.environ['CsysCurses'] = ''
#} cursesExit

class MenuLine(Csys.CSClass): #{
	'''Individual Menu Line

	The essential parts of this are the prompt, and setting the
	sequence count to zero when starting a new Menu table
	'''
	_attributes = {
		'action'		: None,
		'data'			: None,
	}
	_seq = 0

	def __init__(self, prompt, seq=-1, **kwargs): #{
		Csys.CSClass.__init__(self, True, **kwargs)
		self.promptorig = prompt
		if seq < 0: seq = MenuLine._seq
		self.seq		= seq + 1
		MenuLine._seq	= self.seq
		self.addok = self.insok = self.modok = self.delok = True
	#} __init__

	def __cmp__(self, other): return(cmp(self.seq, other.seq))

	def prompt(self): #{
		'''Prompt with sequence number'''
		s = self.promptorig
		if not s: s = str(self.data)
		return ('%2d. %s' % (self.seq, s))
	#} prompt

	def __str__(self): #{
		s = self.promptorig
		if not s: s = str(self.data)
		return s
	#} __str__

	def setSeq(self, seq=0): MenuLine._seq = seq

	def __cmp__(self, other): #{
		'''This should allow sorting arrays of MenuLines'''
		return(cmp(self.seq, other.seq))
	#} __cmp__

#} class MenuLine

_twodigits = re.compile(r'^\d{1,2}$')

class Menu(Csys.CSClass): #{
	'''General Menu Class'''
	_attributes = {
		'nlines'	: term_lines_avail,
		'ncol'		: term_co,
		'begin_y'	: term_firsty,
		'begin_x'	: 0,
		'vcenter'	: True, # vertical centering
		'menuname'	: '',
	}
	def __init__(self, title, menuLines, **kwargs): #{
		self.title		= title
		self.menuLines	= menuLines
		Csys.CSClass.__init__(self, True, **kwargs)
		if not self.menuname: #{
			self.menuname = title.split()[-1].lower()
		#}
		self.win		= curses.newwin(
			self.nlines, self.ncol, self.begin_y, self.begin_x
		)
		self.max_y, self.max_x = self.win.getmaxyx()
		windows_title_set(title, refresh=True)
		self._setsizes()
	#} __init__

	def _setsizes(self): #{
		self.noEntries	= len(self.menuLines)
		assert self.noEntries > 0, 'Menu: menuLines is empty'
		self.columns	= 1 + int(self.noEntries / (self.nlines - 2))
		self.colwidth	= int((self.ncol - 2)/self.columns)
		self.first_x	= 2
		self.first_y	= 0

		# every menu line should have a pointer to its parent
		for menu in self.menuLines: menu.menu = self

		if self.columns == 1: #{{
			'''Find the maximum length to center lines'''
			maxlgth = 0
			for menu in self.menuLines: #{
				lgth = len(menu.prompt()) + 4
				if lgth > maxlgth: maxlgth = lgth
			#}
			self.first_x = 2 + int((self.ncol - maxlgth)/2)

			if self.vcenter: self.first_y = max(0, int((self.max_y - 2 - self.noEntries)/2))

			self._maxlgth = min(self.ncol - 2, maxlgth)
		#}
		else: #{
			self._maxlgth = self.colwidth - 4
		#}}
		self.curindex	= 0 # index into menuLines
		self.str		= ''
	#} _setsizes

	_menuStack = []

	def topMenu(self): #{
		'''Return top of menu stack'''
		global _menuStack
		if Menu._menuStack: return Menu._menuStack[-1]
		return None
	#} topMenu

	def __str__(self): #{
		'''This is for compatibility with instring ubuf'''
		return(self.str)
	#} __str__

	def _deleteWindowsBody(self): #{
		'''Delete existing menu instance from windows_body'''
		windows_body_remove(self.win)
	#} _deleteWindowsBody

	def insertWindowsBody(self): #{
		'''Insert Menu at top of windows stack'''
		self._deleteWindowsBody() # delete old copy
		windows_body.append(self.win)
	#} insertWindowsBody

	def display(self, border=True): #{
		'''Display Menu and refresh)'''
		x				= self.first_x
		y				= self.first_y
		max_y, max_x	= (self.max_y, self.max_x)
		y_max = max_y - 2
		attr			= a_normal
		if border: self.win.border()
		for i in range(len(self.menuLines)): #{
			line = self.menuLines[i]
			y += 1
			if y >= y_max: #{
				y = 1
				x += self.colwidth
			#}
			if i == self.curindex: attr = a_standout
			self.win.move(y, x)
			self.win.addstr(line.prompt()[:self._maxlgth], attr)
			attr = a_normal
		#}
		self.win.refresh()
	#} display

	def addMenuLine(self, MenuLine): #{
		'''Add menu line'''
		self.menuLines.append(MenuLine)
		self._setsizes()
	#} addMenuLine

	def deleteMenuLine(self, MenuLine): #{
		'''Delete MenuLine'''
		try: self.menuLines.remove(MenuLine)
		except ValueError: pass
		else: self._setsizes()
	#} deleteMenuLine

	def getSelection(self): #{
		'''Get selection from menu returning the MenuLine object'''
		menuStack = Menu._menuStack
		if self.title: windows_title_set(self.title, refresh=True)

		if not menuStack or menuStack[-1] != self: menuStack.append(self)
		windows_header_set(scrname=self.displayStack(), refresh=True)

		self.str		= ''
		max_y, max_x	= (self.max_y, self.max_x)
		y				= max_y - 2
		prompt			= 'SELECTION: '
		self.win.move(y, 2)
		self.win.addstr(prompt, a_bold)
		self.display()
		x				= 2 + len(prompt)
		self.insertWindowsBody()
		# Build Prompt
		prompt			= '<ENTER>-Select, <CTRL-L>-redraw'
		if len(menuStack) > 1: #{
			prompt		= prompt + ' <CTRL-P>-prev <CTRL-X>-home'
		#}
		dsp_prmpt(prompt)
		while True: #{
			rc = instring(self.win, x, y, self, max_x - x - 2, attr=a_normal)
			if rc == ENTER: #{
				# Return the appropriate MenuLine object
				rc = self.menuLines[self.curindex]
				break
			#}
			if rc == SUCCEED: #{
				if _twodigits.match(self.str): #{
					ndx = int(self.str) - 1
					if (ndx >= 0 and ndx < self.noEntries): #{
						self.curindex = ndx
						# Return the appropriate MenuLine object
						rc = self.menuLines[self.curindex]
						break
					#}
					unerrs("getSelection: invalid integer = %d" % ndx)
					continue
				#}
				rc = self.str
				break
			#}
			if rc == UPKEY: #{
				self.curindex -= 1
				if self.curindex < 0: self.curindex = self.noEntries - 1
				self.display()
				continue
			#}
			if rc == DOWN_ARROW: #{
				self.curindex += 1
				if self.curindex >= self.noEntries: self.curindex = 0
				self.display()
				continue
			#}
			if rc == KEY_REDRAW: #{
				windows_refresh(redraw=True)
				continue
			#}
			if rc in (EXIT_NOW, HOME_KEY): #{
				while(len(menuStack) > 1): menuStack.pop()
				rc = menuStack[0]
				break
			#}
			if rc == KEY_PREV: #{
				if len(menuStack) <= 1: continue
				menuStack.pop() # go back one menu
				rc = menuStack[-1] # get top menu
				break
			#}
			unerrs("getSelection: invalid response")
			print rc
		#}
		dsp_prmpt('')
		windows_body.pop()
		return(rc)
	#} getSelection

	def displayStack(self): #{
		'''Display the path to our current menu'''
		menuStack = Menu._menuStack
		prompt = '->'.join([x.menuname for x in menuStack])
		return prompt
	#} displayStack

#} class Menu

_keyMenuScroll = {
	curses.KEY_UP		: KeyUPKEY,
	ascii.LF			: KeyENTER,		# ctrl-j
	curses.KEY_DOWN		: KeyDOWN_ARROW,
	curses.KEY_F4		: KeySAVE,
	curses.KEY_NPAGE	: KeyPGDOWN,
	ord('n')			: KeyPGDOWN,
	curses.KEY_PPAGE	: KeyPGUP,
	ord('p')			: KeyPGUP,
	ascii.CAN			: KeyEXIT_NOW,		# ctrl-x
	ascii.FF			: KeyREDRAW,		# ctrl-l
	curses.KEY_HOME		: KeyHOME,
	curses.KEY_END		: KeyEND,
	ascii.TAB			: KeyTAB,
	curses.KEY_RIGHT	: KeyTAB,
	curses.KEY_BTAB		: KeyBTAB,
	curses.KEY_LEFT		: KeyBTAB,
	# vi key equivalents.
	ord('k')			: KeyUPKEY,
	ord('j')			: KeyDOWN_ARROW,
} # _keyMenuScroll

class UserPrompt(object): #{
	'''User Prompts'''
	def __init__(self, key, prompt): #{
		self.key	= key.lower()
		self.prompt	= prompt.strip()
	#}
	def __str__(self): return self.prompt
#} UserPrompt

class MenuScroll(Csys.CSClass): #{
	'''Scrolling Menu Class'''
	addmethod	= None # add line below current position
	insmethod	= None # insert line above current position
	modmethod	= None # modify current record
	delmethod	= None # delete current record

	_attributes = {
		'hdrLine'		: None,
		'border'		: False,
		'vcenter'		: True,	# vertical centering
		'win'			: None,
		'nlines'		: term_lines_avail,
		'ncol'			: term_co,
		'begin_y'		: term_firsty,
		'begin_x'		: 0,
		'userPrompts'	: [],
		'keymap'		: _keyMenuScroll,
		'menuname'		: '',
	}
	def __init__(self, title, menuLines, **kwargs): #{
		Csys.CSClass.__init__(self, True, **kwargs)

		self.title		= title
		if title: #{
			windows_title_set(title, refresh=True)
			if not self.menuname: #{
				self.menuname = title.split()[-1].lower()
			#}
		#}

		if not self.win: self.win = curses.newwin(
			self.nlines, self.ncol, self.begin_y, self.begin_x
		)
		if self.border: #{
			self.win.border()
			self.border	= 1
		#}
		else: #{
			self.border = 0
		#}
		max_y, max_x = self.win.getmaxyx()
		self.nlines = max_y - 2 * self.border
		self.ncol	= max_x - 2 * self.border

		if self.hdrLine: #{{
			# limit to window width
			self.hdrLine = hdrLine = self.hdrLine[:self.ncol - 2*self.border]
			self._hdrLine_x = (self.ncol - len(hdrLine))/2
			self.win.move(self.border, self._hdrLine_x)
			self.win.addstr(hdrLine)
			self.win.noutrefresh()
			self.nlines -= self.border

			self.winbody	= self.win.derwin(
				self.nlines, self.ncol,
				1 + self.border, self.border
			)
			# self.winbody.border()
			# self.winbody.noutrefresh()
		#}
		else: #{
			if self.border: #{
				self.winbody = self.win.derwin(
					self.nlines, self.ncol,
					self.border, self.border
				)
			#}
			else: self.winbody	= self.win
		#}}
		if self.winbody != self.win: self.win.noutrefresh()
		self.max_y, self.max_x = self.winbody.getmaxyx()

		# assert len(menuLines) > 0, 'Menu: menuLines is empty'
		self.menuLines	= menuLines	# This may change with pattern matches
		self.origLines	= menuLines	# this will be saved
		self.curindex	= 0
		self._setsizes()
		self.str		= ''
		self.pattern	= None
		# These are methods that will enable add, modify, and delete
		# The will be called with the menuLine object as the argument
		# so may be direct methods of the menuLine class.
		self.enterok	= False
		self.extrakeys = []
		for p in self.userPrompts: self.extrakeys.append(p.key)
		
		# every menu line should have a pointer to its parent
		for menu in self.menuLines: menu.menu = self
	#} __init__

	def set_first_ndx(self, first_ndx): #{
		'''Set first index and max index in display'''

		# make sure first_ndx is in range
		first_ndx		= max(0, first_ndx)
		self.first_ndx	= first_ndx = min(self.maxindex, first_ndx)
		self.high_ndx	= min(first_ndx + self.max_y, self.noEntries) - 1
		return self.first_ndx
	#} set_first_ndx

	def set_curindex(self, curindex): #{
		'''Set curindex, modifying self.low_ndx, etc.'''

		if self.curindex != curindex: #{
			max_y, max_x	= (self.max_y, self.max_x)
			# make sure curindex is in range
			curindex = max(0, curindex)
			curindex = min(self.maxindex, curindex)

			# we are in the current screen.
			if self.first_ndx <= curindex <= self.high_ndx: #{{
				try: # {{ redraw last current index with normal attributes
					line = self.menuLines[self.curindex]
					self.winbody.move(line.cur_y, line.cur_x)
					self.winbody.addstr(line.prompt(), a_normal)
				#}
				except: pass #}
				try: #{{
					self.curindex = curindex
					line = self.menuLines[self.curindex]
					self.winbody.move(line.cur_y, line.cur_x)
					self.winbody.addstr(line.prompt(), a_standout)
				#}
				except: pass #}
			#}
			else: #{
				self.curindex = curindex
				if curindex < self.first_ndx: self.set_first_ndx(curindex)
				elif curindex > self.high_ndx: self.set_first_ndx(1 + curindex - max_y)
				self.display()
			#}}
		#}
		return self.curindex
	#} set_curindex

	def _setsizes(self, last=False): #{
		'''Set array sizes'''

		self.noEntries	= len(self.menuLines)
		self.maxindex	= self.noEntries - 1
		'''Find the maximum length to center lines'''
		maxlgth = 0
		for menu in self.menuLines: #{
			lgth = len(menu.prompt())
			if lgth > maxlgth: maxlgth = lgth
		#}
		max_y, max_x	= (self.max_y, self.max_x)
		self.first_x	= max(0, int((max_x - maxlgth)/2))

		self.first_y = 0
		if self.vcenter: self.first_y = max(0, int((max_y - self.noEntries)/2))

		self._maxlgth	= min(max_x -2, maxlgth)
		first_ndx	= 0
		if last: #{ Point to bottom line of menu
			first_ndx = min(self.noEntries, max_y) - 1
		#}
		self.curindex = self.set_first_ndx(first_ndx)
		self.display()
	#} _setsizes

	def reload(self): #{
		'''Reset sizes'''
		self.menuLines = self.origLines
		self._setsizes()
	#}

	def __str__(self): #{
		'''This is for compatibility with instring ubuf'''
		return(self.str)
	#} __str__

	def _deleteWindowsBody(self): #{
		'''Delete existing menu instance from windows_body'''
		windows_body_remove(self.win)
	#} _deleteWindowsBody

	def insertWindowsBody(self): #{
		'''Insert Menu at top of windows stack'''
		self._deleteWindowsBody() # delete old copy
		windows_body.append(self.win)
	#} insertWindowsBody

	def display(self): #{
		'''Display Menu and refresh)'''
		max_y, max_x	= (self.max_y, self.max_x)
		attr			= a_normal
		self.winbody.clear()
		if self.hdrLine: #{
			self.win.move(self.border, self._hdrLine_x)
			self.win.addstr(self.hdrLine)
		#}

		x	= self.first_x

		if self.noEntries > 0: #{
			highlight_y = self.curindex - self.first_ndx + self.first_y
			self.curmenu = self.menuLines[self.curindex]

			for y in range(self.first_y, max_y): #{
				i = y - self.first_y + self.first_ndx
				if i > self.maxindex: break
				line = self.menuLines[i]
				if y == highlight_y: attr = a_standout
				line.cur_y, line.cur_x = (y, x)
				self.winbody.move(y, x)
				self.winbody.addstr(line.prompt()[:self._maxlgth], attr)
				attr = a_normal
			#}
			self.winbody.move(highlight_y, x)
		#}
		if self.border: self.win.border()
		self.win.noutrefresh()
		self.winbody.noutrefresh()
	#} display

	def _getpattern(self): #{
		'''Prompt for pattern'''
		win = win_command
		max_y, max_x	= win.getmaxyx()
		prompt			= 'PATTERN: '
		x				= len(prompt) + 2
		win.move(0, 2)
		win.addstr(prompt)
		while True: #{
			self.str = ''
			rc = instring(win, x, 0, self, max_x - x - 3,
				ext_results=False, attr=a_normal
			)
			if rc == ENTER: #{
				self.pattern = ''
				break
			#}
			if rc != SUCCEED: #{
				unerrs('Invalid Return Code %d' % rc)
				continue
			#}
			cmd = 're.compile(%s, re.IGNORECASE)' % repr(self.str)
			try: rc = eval(cmd) #{
			except: #{
				unerrs('Invalid Pattern %s' % self.str)
				continue
			#}}
			if rc: #{
				self.pattern = rc
				break
			#}
		#}
		win.clear()
		win.noutrefresh()
		return rc
	#} _getpattern

	def _selectPattern(self, last=False): #{
		'''Select Menu Lines matching self.pattern'''

		# save for possible restoration
		try: curindex = self.menuLines[self.curindex].seq - 1
		except: curindex = 0

		if self.pattern: #{{
			pattern = self.pattern
			self.menuLines = []
			for line in self.origLines: #{
				if pattern.search(str(line)): self.menuLines.append(line)
			#}
			if not self.menuLines: #{
				unerrs('No matches')
				self.menuLines = self.origLines
			#}
		#}
		else: #{
			self.menuLines = self.origLines
		#}}
		# print 'len menuLines = %d' % len(self.menuLines)
		self._setsizes(last)
		if self.menuLines == self.origLines: self.set_curindex(curindex)
	#} _selectPattern

	def _deleteMenuLine(self, menuLine): #{
		'''Delete menuLine from original and selected lines'''

		returnLine = None
		if self.origLines != self.menuLines: #{
			try: #{{
				ndx = self.menuLines.index(menuLine)
			#}
			except ValueError: #{
				pass
			#}
			else: #{
				deleted = self.menuLines.pop(ndx)
				if self.menuLines: #{{
					curindex = self.curindex
					self._setsizes()
					self.set_curindex(min(curindex, self.maxindex))
					returnLine = self.menuLines[self.curindex]
				#}
				else: #{
					self.menuLines = self.origLines
				#}}
			#}}
		#}
		try: ndx = self.origLines.index(menuLine)
		except ValueError: return returnLine

		deleted = self.origLines.pop(ndx)
		if self.origLines == self.menuLines: #{
			curindex = self.curindex
			self.setsizes()
			if returnLine: #{{
				self.set_curindex(self.maxindex)
			#}
			else: #{
				self.set_curindex(min(curindex, self.maxindex))
			#}}
			returnLine = self.menuLines[self.curindex]
		#}
	#} _deleteMenuLine

	def _goto(self, c): #{
		'''Go to number selected'''
		win				= win_command
		max_y, max_x	= win.getmaxyx()
		self.str		= chr(c)
		# print '_goto: start >%s<' % self.str
		while True: #{
			prompt		= 'Enter Line Number: '
			x			= len(prompt) + 2
			win.move(0, 2)
			win.addstr(prompt)
			rc = instring(win, x, 0, self, max_x - x - 3,
				i=len(self.str), ext_results=False, attr=a_normal
			)
			if rc == ENTER or rc == EXIT_NOW: break
			if rc != SUCCEED: #{
				unerrs('Invalid Return Code %d' % rc)
				continue
			#}
			seq = int(self.str)
			# print 'seq = %d' % seq
			for i in range(len(self.menuLines)): #{{
				line = self.menuLines[i]
				# print 'line.seq = %d' % line.seq
				if line.seq == seq: #{
					if not self.first_ndx <= i < self.first_ndx + self.nlines: #{
						self.set_first_ndx(i)
					#}
					self.set_curindex(i)
					rc = line
					break
				#}
			#}
			else: #{
				unerrs('Invalid sequence %d' % (seq))
				self.str = ''
				continue
			#}}
			break
		#}
		win.clear()
		win.noutrefresh()
		return rc
	#} _goto

	def getSelection(self): #{
		'''Get selection from menu returning the MenuLine object'''

		self.str = ''
		max_y, max_x	= (self.max_y, self.max_x)
		# This will set this window to the top of the stack.  It
		# will be left there at the end so that we can display
		# multiple scrolling areas side by side for things like
		# selections, moving from the left window to the right.
		self.insertWindowsBody()
		curses.doupdate()
		while True: #{
			# Build Prompt
			prompt = '<^L>Redraw </>Search'
			if self.enterok:							prompt += ' <ENTER>Select'
			if self.first_ndx:							prompt += ' [P]rev'
			if self.first_ndx + max_y < self.noEntries:	prompt += ' [N]ext'
			if self.addmethod:							prompt += ' [A]dd'
			if self.modmethod:							prompt += ' [M]odiify'
			if self.delmethod:							prompt += ' [D]elete'
			for p in self.userPrompts:					prompt += ' ' + str(p)

			dsp_prmpt(prompt)
			self.display()
			self.winbody.refresh()
			try: c = wgetchar(self.winbody, self.keymap) #{
			except KeyENTER: #{
				if not self.enterok: #{
					curses.beep()
					continue
				#}
				# Return the appropriate MenuLine object
				rc = self.menuLines[self.curindex]
				break
			except KeyUPKEY: #}{
				curindex = self.curindex - 1
				if curindex < 0: #{
					curses.beep()
					continue
				#}
				self.set_curindex(curindex)
				continue
			except KeyDOWN_ARROW: #}{
				curindex = self.curindex + 1
				if curindex > self.maxindex: #{
					curses.beep()
					continue
				#}
				self.set_curindex(curindex)
				continue
			except KeyREDRAW: #}{
				windows_refresh(redraw=True)
				continue
			except KeyEXIT_NOW: #}{
				rc = EXIT_NOW
				break
			except KeyPGDOWN: #}{
				first_ndx = min(self.maxindex, self.high_ndx + max_y - 1)
				if first_ndx == self.first_ndx: #{
					curses.beep()
					continue
				#}
				self.set_curindex(first_ndx)
				continue
			except KeyPGUP: #}{
				if self.first_ndx == 0: #{
					curses.beep()
					continue
				#}
				self.set_curindex(max(0, self.first_ndx - max_y + 1))
				continue
			except KeyHOME: #}{
				self.set_curindex(0)
				continue
			except KeyEND:	#}{
				self.set_curindex(self.maxindex)
				continue
			except KeyTAB: #}{
				rc = KEY_TAB
				break
			except KeyBTAB: #}{
				rc = KEY_BTAB
				break
			else: #}{
				if ascii.isdigit(c): #{
					self._goto(c)
					continue
				#}
				if ascii.isascii(c): rc = chr(c).lower()
				curMenuLine = self.menuLines[self.curindex]
				if rc == 'd' and self.delmethod: #{
					if not curMenuLine.delok: #{
						unerrs('Delete Not Allowed')
						continue
					#}
					if self.delmethod(curMenuLine) != SUCCEED: #{
						curses.beep()
						continue
					#}
					# This test will be true if there are lines left
					if(self._deleteMenuLine(curMenuLine)): continue

					# This will make the next test True so fall through
					# into the add mode.
					rc = 'a'
				#}
				if rc == 'a' and self.addmethod: #{
					if not curMenuLine.addok: #{{
						unerrs('Add Not Allowed')
					#}
					else: #{
						self.addmethod(curMenuLine)
						self.pattern = None
						self._selectPattern(last=True)
					#}}
					continue
				#}
				if rc == 'i' and self.insmethod: #{
					if not curMenuLine.insok: #{{
						unerrs('Insert Not Allowed')
					#}
					else: #{
						self.insmethod(curMenuLine)
						self.pattern = None
						self._selectPattern(last=True)
					#}}
					continue
				#}
				if rc == 'm' and self.modmethod: #{
					if not curMenuLine.modok: #{{
						unerrs('Modify Not Allowed')
					#}
					else: #{
						self.modmethod(curMenuLine)
					#}}
					continue
				#}
				if rc == '/': #{
					pattern = self._getpattern()
					self._selectPattern()
					continue
				#}
				if rc == 'q': #{
					rc = EXIT_NOW
					break
				#}
			#}}
			if rc in self.extrakeys: break
			print self.extrakeys
			unerrs("getSelection: invalid response >%s<" % rc)
		#}
		dsp_prmpt('')
		# windows_body.pop()
		return(rc)
	#} getSelection

	def displayStack(self): #{
		'''Display the path to our current menu'''
		menuStack = Menu._menuStack
		prompt = '->'.join([x.menuname for x in menuStack])
		return prompt
	#} displayStack

#} MenuScroll

class textMenuLine(Csys.CSClass): #{
	'''Text Menu Line with prompt'''

	_seq = 0
	_attributes = {
		'fmt'	: '%s: %s',
		'seq'	: -1,
		'y'		: 0,
		'x'		: 0,
	}
	def __init__(self, data, lgth, **kwargs): #{
		global _seq
		self.data		= data
		self.len		= lgth
		Csys.CSClass.__init__(self, True, **kwargs)
		if self.seq < 0: self.seq = _seq
		self.seq		+= 1
		_seq			= self.seq
		self.trim		= data.name
		self.data_x		= self.x + len(self.trim) + 1
		self.fmt		= '%2d. ' + self.fmt
	#} __init__

	def prompt(self): return(self.fmt % (self.seq, self.trim, self.data))
	
#} textMenuLine

import Csys.Fields

class ScreenField(Csys.CSClass): #{
	'''Screen Field from scan'''
	_attributes = {
		'data'			: None, # data in internal format
		'displen'		: None, # displen (overridden by fdesc)
		'fdesc'			: None, # field description (empty if prompt)
		# 'inpfunc'		: None, # Input Value
		# 'postfunc'	: None, # Post Processing Function
		# 'prefunc'		: None, # Preprocessing Function
		'prompt'		: None, # text for prompt
		'screen'		: None, # parent screen
		'x'				: 0, # x, y co-ordinates relative to window
		'y'				: 0,
		'_index'		: 0, # Index into Screens field table
		'lastdata'		: None, # for Recall
		'origdata'	:	 None, # original from database/config
	} # _attributes

	def __init__(self, y, x, **kwargs): #{
		Csys.CSClass.__init__(self, True, **kwargs)
		self.y = y
		self.x = x
	#} __init__

	def setOrigData(self, val): #{
		'''Set original data values'''
		try: val = self.fdesc.set(val)
		except: val = None
		self.data = self.lastdata = self.origdata = val
	#} setOrigData

	def __str__(self): #{
		'''Return string or prompt'''
		if self.prompt: return self.prompt
		return str(self.data)
	#} __str__

	def __setattr__(self, attr, val): #{
		'''Set attributes, converting data if necessary'''
		cols = self.__dict__
		try: #{{
			if attr == 'data' and self.fdesc: val = self.fdesc.set(val)
			cols[attr] = val
		#}
		except: #{
			unerrs('ScreenFields: failed field %s' % self.fdesc.lname)
			# cols[attr] = self.fdesc.set('')
		#}}
	#} __setattr__

	# def __cmp__(self, other): return(cmp(self.data, other.data))

	def displayField(self): #{
		'''Display field, suppressing password fields'''
		fdesc = self.fdesc
		if fdesc: #{
			s = fdesc.fmt % self.data
			if fdesc.passwd: s = '*' * len(s)
			self.screen.window.move(self.y, self.x)
			self.screen.window.addstr(s)
		#}
	#} displayField

#} ScreenField

class NoFields(Error): #{
	'''Raised when there are no data fields in screen'''
	def __init__(self, screen): #{
		Error.__init__(self, 'No fields: %s' % (screen.scrname,))
		self.screen = screen
	#}
#} NoFields

class NextFieldName(Error): #{
	'''Exception to jump to speficied field Name'''
	def __init__(self, fname): #{
		'''Called by Screen.inpfunc to jump to a field'''
		self.msg = 'Jump to field >%s< failed' % fname
		Error.__init__(self, msg)
		self.screen = screen
		self.fname = fname
	#}
#} NextField

class BadData(Error): #{
	def __init__(self, field, msg): #{
		'''Bad Data in field'''
		Error.__init__(self, msg)
		self.field	= field
		self.msg	= msg
	#}
#} BadData

class NeedData(Error): #{
	def __init__(self, field, msg=None): #{
		'''Need Data in field'''
		if msg is None: msg = 'Need data'
		self.msg = msg
		Error.__init__(self, msg)
		self.field	= field
	#}
#} NeedData

class SaveRequested(Error): #{
	def __init__(self, field, ier): #{
		'''SAVE, EXIT_NOW pressed'''
		Error.__init__(self, 'Save requested = %d' % ier)
		self.ier = ier
	#}
#} SaveRequested

class SimpleKeyException(Error): #{
	__doc__ = Csys.detab('''
	Base class for key press exceptions that will save the field and return
	value from the instring function.

	The screen may be found from the field.screen attribute.
	''')
	def __init__(self, field, ier): #{
		'''Set class paramaters'''
		self.field = field
		self.ier = ier
	#} __init__
#} SimpleKeyException

class RecallData(SimpleKeyException): pass

class PreviousFieldCancel(SimpleKeyException): pass

class HomeKey(SimpleKeyException): pass

class EndKey(SimpleKeyException): pass

class EnterKey(SimpleKeyException): pass

class UnknownKey(SimpleKeyException): pass

_ExceptionMap = {
	RECALL		: RecallData,
	UPKEY		: PreviousFieldCancel,
	HOME_KEY	: HomeKey,
	KEY_END		: EndKey,
	# ENTER		: EnterKey,
	# DOWN_ARROW	: EnterKey,
}

class Screen(Csys.CSClass): #{
	'''Screen Structure'''
	_attributes = {
		'cur_motion':	1,	# plus or minus one cursor motion
		'cur_x':		0,	# current x, y co-ordinates
		'cur_y':		0,
		'fields':		[], # array of ScreenField objects
		'fname':		'',	# file name to load screen
		'max_x':		0,	# max x, y, co-ordinates
		'max_y':		0,
		'scrname':		'', # screen name for display
		'title':		'', # Screen Title
		'top_x':		0, # Top x, y co-ordinates
		'top_y':		term_firsty,
		'window':		None,
		'configfiles':	None, # list of configuration files to parse
		'rec':			{},
		'border':		False,
		'hcenter':		False, # horizontal center
		'vcenter':		False, # vertical center
	} # _attributes

	def __init__(self, **kwargs): #{
		'''Initialize Screen Object'''
		Csys.CSClass.__init__(self, True, **kwargs)
		self.keycancel	= False
		if self.fname: self.getfile()
		self._nfields	= len(self.fields)
		self._genFieldMap()
		if not self.window and self._nfields: #{
			if self.vcenter: #{
				self.top_y = max(term_firsty, int((term_lasty - self.max_y) / 2))
			#}
			if self.hcenter: #{
				self.top_x = max(0, int((term_co - self.max_x) / 2))
			#}
			self.window = curses.newwin(
				self.max_y, self.max_x,
				self.top_y, self.top_x
			)
		#}
		if self.window: #{
			self.max_y, self.max_x = self.window.getmaxyx()
			if self.border: self.window.border()
			self.displayAll()
		#}
	#} __init__

	def _genFieldMap(self): #{
		for i in range(len(self.fields)): #{
			field = self.fields[i]
			field.index = i
			field.screen = self
			if field.fdesc: #{
				fdesc = field.fdesc
				rname, lname = fdesc.rname, fdesc.lname
				self.rec[lname] = field
				if rname: #{
					key = '%s.%s' % (rname, lname)
					self.rec[key] = field
					key = key.replace('.', '_', 1)
					self.rec[key] = field
				#}
			#}
		#}
	#} _genFieldMap

	def displayAll(self, prompts=True, data=True, rname=None, lname=None): #{
		'''Display Prompt Fields'''
		win = self.window
		if prompts: win.clear()
		for field in self.fields: #{
			if prompts and field.prompt: #{
				try: #{{
					win.move(field.y, field.x)
					win.addstr(field.prompt, a_dim)
				#}
				except: #{
					unerrs('win.addstr(%d, %d) failed' % (field.y, field.x))
					unerrs('prompt >%s<' % field.prompt)
				#}}
			#}
			fdesc = field.fdesc
			if data and fdesc: #{
				if rname and fdesc.rname != rname: continue
				if lname and fdesc.lname != lname: continue
				field.displayField()
			#}
		#}
		if self.border: win.border()
	#} displayPrompts

	def displayPrompts(self): #{
		'''Display Prompt Fields'''
		self.displayAll(data = False)
	#} displayPrompts

	def displayData(self, rname=None, lname=None): #{
		'''Display Prompt Fields'''
		self.displayAll(prompts = False, rname=rname, lname=rname)
	#} displayData

	def getfile(self, fname=None): #{
		'''Read file info from file'''
		if fname is None: fname = self.fname
		from cStringIO import StringIO

		config = ''
		Fields = self.fields
		if hasattr(fname, 'readlines'): fh = fname
		else: fh = open(fname)

		in_metadata = False

		if self.border: border = 1
		else: border = 0

		y = border - 1

		pat = re.compile(r'^(\s*)([^[]*)\[([^[]*)\]')

		from Csys.Edits import detab

		for line in fh: #{
			if in_metadata: #{
				config += line.strip() + '\n'
				continue
			#}
			if line.startswith('%metadata'): #{
				in_metadata = True
				continue
			#}
			y += 1
			line = detab(line) # change tabs to spaces
			x = border
			while line: #{
				line = line.rstrip()
				if not line: break
				n = len(line)
				if n > self.max_x: self.max_x = n
				R = pat.match(line)
				if not R: #{
					Fields.append(ScreenField(y, 0, prompt = line))
					break
				#}
				lb, p, f = R.groups()
				x += len(lb)
				if p: #{
					Fields.append(ScreenField(y, x, prompt = p.rstrip()))
					x += len(p)
				#}
				x += 1 # space past left bracket
				# This loop permits pipe symbols ``|'' to split fields
				# leaving only a single space between them instead of
				# using ``]['' which would take two spaces.
				for p in f.split('|'): #{
					displen = len(p)
					Fields.append(ScreenField(y, x,
						data	= p.strip(),
						displen	= displen)
					)
					x += displen + 1 # space past delimiter
				#}
				line = pat.sub('', line).rstrip()
			#}
		#}
		fh.close()
		self.max_y = y + 1 + border

		cfg = Csys.ConfigParser()

		# This will either parse a list of configuration files or a single
		# string.
		if self.configfiles: #{{
			from tempfile import NamedTemporaryFile
			f = NamedTemporaryFile() # create temp file readable by config
			f.write(config)
			f.flush() # need to flush so config.read works
			cfg.read(tuple(self.configfiles + (f.name, )))
		#}
		else: #{
			fh = StringIO(config)
			cfg.readfp(fh)
			# fh.seek(0)
			# fhout = Csys.openOut('/tmp/debug.conf')
			# for line in fh.readlines(): fhout.write(line)
			# fhout.close()
		#}}
		cfgAll		= cfg.getAll()
		cfgDefaults	= cfgAll['default']
		max_x		= 0
		sections	= cfg.sections()
		for field in Fields: #{
			if field.prompt: #{{
				x = field.x + len(field.prompt)
			#}
			elif field.data: #{
				section = field.data

				# args = cfg.getDict(section)
				args = cfgAll.get(section, cfgDefaults)
				for key in ('passwd', ): #{
					if key in args: #{
						try: args[key] = cfg.getboolean(section, key)
						except: args[key] = False
					#}
				#}
				fdesc = field.fdesc = Csys.Fields.FieldDesc(
					rname		= args.get('rname', section),
					lname		= args.get('lname', section),
					type		= args['type'],
					edit		= args.get('edit', ''),
					displen		= field.displen,
					description	= args.get('description', ''),
					passwd		= args.get('passwd', False)
				)
				field.data = args.get('default')
				x = field.x + field.displen
			#}}
			if x > max_x: max_x = x
		#}
		self.max_x = max_x + border
		self._nfields = len(self.fields)
	#} getfile

	# this is a place-holder for replacement when sub-classed
	skip_always = tuple()

	def prefunc(self, field): return(0)

	def inpfunc(self, field): #{
		'''Get field input'''
		y, x = (field.y, field.x)
		dsp_prmpt('Enter: %s' % field.fdesc.description)
		rc = instring(field.screen.window, x, y, field, field.displen)
		dsp_prmpt('')
		if rc == KEY_CANCEL: raise KeyCANCEL
		return rc
	#} inpfunc

	key_fields = tuple()

	def postfunc(self, field, ier): #{
		exception = _ExceptionMap.get(ier)
		if exception: raise exception(field, ier)
		
		if ier == ENTER and field in self.key_fields: #{
			raise NeedData(field)
		#}
		if ier in (SUCCEED, SAVE, EXIT_NOW, ENTER, DOWN_ARROW): #{
			fdesc = field.fdesc
			try: data = fdesc.set(field.str) #{
			except: #{
				msg = ('invalid data >%s< field >%s<' % (field.str, fdesc.lname))
				raise BadData(field, msg)
			#}}
			if data == field.data: #{
				if ier == SUCCEED: raise EnterKey(field, ier) # hasn't changed
			#}
			else: field.data = data
			if not ier in (SUCCEED, ENTER, DOWN_ARROW): raise SaveRequested(field, ier)
			return
		#}
		raise UnknownKey(field, ier)
	#} postfunc

	def chkcomplete(self): return None

	def getFieldByName(self, fname): #{
		'''Get field with lname matching fname'''
		for field in self.fields: #{
			if field.fdesc and field.fdesc.lname == fname: return field
		#}
		return None
	#} getFieldByName

	def getData(self): #{
		'''Parse data fields from screen'''
		maxfield		= self._nfields - 1
		assert maxfield > 0, 'Screen.getData:: no fields'
		self.nodata		= True
		self.keycancel	= False
		win = self.window
		global windows_body
		saveWindowsBody	= windows_body[:]
		windows_body	= [win]
		self.displayAll()
		windows_refresh(redraw=True)
		self.cur_motion	= 1		# direction of motion
		cur_motion = i = 0 # first field
		self.save_requested = False
		# save data to origdata
		for field in self.fields: field.origdata = field.data

		while not self.save_requested: #{
			if cur_motion: #{
				i += cur_motion
				if i > maxfield: #{{
					if self.nodata: raise NoFields(self)
					i = 0
				#}
				elif i < 0: #{
					i = maxfield
				#}}
			#}
			cur_motion = self.cur_motion
			field = self.fields[i]
			fdesc = field.fdesc
			if fdesc is None: continue
			try: #{{
				rc = self.prefunc(field)
				if rc: #{
					self.cur_motion = cur_motion = rc
					continue
				#}
				self.nodata = False
				cur_motion = self.cur_motion = 1
				ier = self.inpfunc(field)
				self.postfunc(field, ier)
			#}
			except KeyCANCEL: #{
				self.keycancel = self.save_requested = True
				# restore data from origdata
				for field in self.fields: field.data = field.origdata
			#}
			except BadData, rc: #{
				unerrs(rc.msg)
				cur_motion = 0
			#}
			except NeedData, rc: #{
				unerrs(rc.msg)
				cur_motion = 0
			#}
			except SaveRequested, rc: #{
				next_field = self.chkcomplete()
				if next_field: #{{
					field = self.rec[next_field]
					cur_motion = 0
				#}
				else: #{
					self.save_requested = True
					# update lastdata for subsequent RECALLs
					for field in self.fields: field.lastdata = field.data
				#}}
			#}
			except RecallData: #{
				field.data = field.lastdata
				cur_motion = 0
			#}
			except PreviousFieldCancel: #{
				cur_motion = self.cur_motion = -1
			#}
			except HomeKey: #{
				cur_motion = i = 0
			#}
			except EndKey: #{
				i = maxfield			# place pointer on last field
				cur_motion = 0			# don't change it.
				self.cur_motion = -1	# step backwards.
			#}
			except NextFieldName, rc: #{
				field = self.rec[rc.fname]
				i = field.index
				cur_motion = 0
				continue
			#}
			except EnterKey, rc: #{
				pass
			#}}
			field.displayField()
		#}
		windows_body = saveWindowsBody[:]
	#} getData
#} class Screen

if not _inPyDoc and __name__ == '__main__':
	windows_header_set(title='testing', scrname='progname')
	win_body.addstr('OK')
	prompt_getstr('test prompt: ')
	c = ''
	win_body.keypad(1)
	map=_keyExceptionMap
	while False and c != 'q': #{
		windows_refresh(redraw=True)
		try: #{{
			# c = wgetchar(win_body)
			c = win_body.getch()
			print 'c: ', map.get(c, 'None')
			unerrs('key returned %s' % curses.keyname(c))
			unerrs('key returned 0x%x' % (c))
		#}
		except Exception, e: #{
			unerrs('exception %s' % e)
		#}
		except: #{
			unerrs('unknown exception')
		#}}
		break
	#}
	cursesExit()
