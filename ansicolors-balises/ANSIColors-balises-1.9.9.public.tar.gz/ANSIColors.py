#!/usr/bin/env python
# -*- encoding: utf-8 -*-

""" An efficient and simple ANSI colours module (and also a powerfull script), with functions to print text using colours.

About the convention for the names of the colours :
 * for the eight colours black, red, green, yellow, blue, magenta, cyan, white:
  * the name in minuscule is for colour **with bold** (example 'yellow'),
  * the name starting with 'B' is for colour **without bold** (example 'Byellow'),
  * the name starting with a capital letter is for the background colour (example 'Yellow').
 * for the special effects (blink, italic, bold, underline, negative), **not always supported** :
  * the name in minuscule is for **activate** the effect,
  * the name starting in capital letter is for **desactivate** the effect.
 * for the other special effects (nocolours, default, Default, clear, el), the effect is **immediate** (and seems to be well supported).

List of functions:
==================

To print a string
-----------------

 * sprint: give a string,
 * printc: like __builtin__.print, but with interpreting balises to put colours,
 * writec: like printc, but using any file object (and no new line added at the end of the string),

To clean the terminal or the line
---------------------------------

 * erase: erase all ANSI colours balises in the string (like sprint, but erasing and not interpreting colour balises)
 * clearLine, clearScreen: to clear the current line or screen,
 * Reset: to return to default foreground and background, and stopping all *fancy* effects (like blinking or reverse video).
 
Others functions
----------------

 * notify: try to display a *system* notification. **Only on *linux*.**
 * xtitle: try to set the *title* of the terminal. **Not always supported**.

Example of use (module) :
=========================

 To store a string, use *sprint* (*i.e.* print to a string, sprint), like here ::

   >>> example=sprint("France flag is <blue>blue<white>white<red>red<white>, Italy flag have <green>green on it<white>.")
 The string *example* can then be printed, with colours, with ::

   >>> print example # Sorry, but in the documentation it is hard to show colours :)
   France flag is bluewhitered, Italy flag have green on it.
 
 
 To directly print a string colored by balises, use *printc* ::

   >>> printc("Batman's costum is <black>black<white>, Aquaman's costum is <blue>blue<white> and <green>green<white>.")

 .. seealso::
    This is the most usefull function. To do the same, but on any file, use *writec*
 
 Moreover, the function *erase* can also be usefull to simply delete all *valid* colour balises ::

   >>> print erase("Batman's costum is <black>black<white>, Aquaman's costum is <blue>blue<white> and <green>green<white>, and this is a non-valid <balise>, so it is kept like this.")
   Batman's costum is black, Aquaman's costum is blue and green, and this is a non-valid <balise>, so it is kept like this
 
 
 In this last example, *<el>* balise is used to erase the current content of the line, usefull to make a *dynamical* print ::

   >>> writec("<red>Computing <u>2**(2**(2**4))<reset>...."); tmp=2**(2**(2**4)); writec("<el><green> Done !<reset>")
   Done !
 The first 'Computing 2**(2**(2**4))....' have disappeared after the computation !

Example of use (script):
========================

 * To show the help :code:`$ ANSIColors.py --help`;

 * To run a test :code:`$ ANSIColors.py --test`;

 * To produce a GNU Bash colour aliases file 
   :code:`$ ANSIColors.py --generate --file ~/.colour_aliases.sh`

Auto detection
==============

Now, this script can detect if ANSI codes are supported :
  1. ``$ ANSIColors.py --help`` : will print with colours if colours seems to be supported;
  2. ``$ ANSIColors.py --help --noANSI`` : will print without any colours, even if it is possible;
  3. ``$ ANSIColors.py --help --ANSI`` : will force the use of colours, even they seems to be not supported.

And, the module part behaves exactly like the script part.

**This functionality is still experimental**, and work only on Ubuntu 11.10,
as far as I know.

------------------------------------------------------------------------------

About:
======

This module is **still in development**.
Last version of this project can be found on-line :

 * `here on BitBucket <https://bitbucket.org/lbesson/ansi-colors>`_;
 * `here on PyPi <https://pypi.python.org/pypi/ANSIColors-balises>`_.


The reference page for ANSI code is : `here on Wikipedia <http://en.wikipedia.org/wiki/ANSI_escape_code>`_.
The reference page for XTitle escape code is : `here <http://www.faqs.org/docs/Linux-mini/Xterm-Title.html>`_.

Documentation
=============

The doc is available on-line :

 * on `pythonhosted.org/ANSIColors-balises/ <http://pythonhosted.org/ANSIColors-balises/index.html>`_;
 * on one of my own pages :

   * on the cr@ns network `besson/publis/ansi-colors/ <http://perso.crans.org/besson/publis/ansi-colors/index.html>`_,
   * on the CS department at ENS de Cachan `~lbesson/publis/ansi-colors/ <http://www.dptinfo.ens-cachan.fr/~lbesson/publis/ansi-colors/index.html>`_,

Or some explanations (and an OCaml version of this module) 
are available on my Google Site `tools/ansi-colors <https://sites.google.com/site/naereencorp/tools/ansicolors>`_.

Copyrigths:
===========

 (c) October 2012 - Mars 2013
 By Lilian BESSON,
 ENS de Cachan (M1 Mathematics & M1 Computer Science MPRI)
 mailto:lbesson@ens-cachan.fr
    
 For Naereen Corp.
 mailto:naereen-corporation@laposte.net
 https://sites.google.com/site/naereencorp/tools/ansicolors
"""

#########################
##### Program part ######
#########################

"""\n\
List of all colours:
==================

black, red, green, yellow, blue, magenta, cyan, white:
 Bold colours.

Bblack, Bred, Bgreen, Byellow, Bblue, Bmagenta, Bcyan, Bwhite:
 Normal colours (no bold).

Black, Red, Green, Yellow, Blue, Magenta, Cyan, White:
 Background colours.

blink, Blink:
 Blink special caracters (Blink is faster than blink).

 .. warning::

   Those are **not supported by all terminal emulator**.
   For example, gnome-terminal and terminator **doesn't** support it,
   but mintty.exe (Cygwin Windows terminal) support it.

reset, nocolors:
 Special caracters to reinitialized ANSI codes buffer, or to do nothing.

default, Default:
 default foreground colour, default background colour.

italic, Italic :
 italic on, off.  **Not always supported**.

b, B :
 bold on, off,
 
u, U :
 underline on, off,
 
neg, Neg :
 reverse video on, off. **Not always supported**.

clear:
 try to clear the screen. **Not always supported**.

el:
 try to erase the current line. **Not always supported**.
 Usefull to use with ``sys.stdout.write`` 
 and make the current printed line change !

bell:
 try to make an alarm sound. Also used to end the *xtitle* sequence.

warning, question, WARNING, INFO, ERROR:
 aliases for classic markup (/!\\, /?\\, 'WARNING', 'INFO' and 'ERROR').
"""

__author__='Lilian BESSON (mailto:lilian.besson@normale.fr)'
__version__='1.9.9.public'
__date__='mar. 19/03/2013 at 12h:25m:49s'

#1###############
# Usual Modules #
import os, sys, subprocess

################################################################################
# TODO: arrange this.
# TODO: make them hidden from the interface of the script
# idea: remove from __all__.
########################################
#### Default values for new parsers ####

def _default_epilog(version, date, author):
 """ This return the default epilog used to new parsers,
 which contains a copyright paragraph, determined by the three arguments version, date, author.
 """
 return """\n\

<yellow>Copyrigths:
===========<reset>
   Version %s, (c) 2012-2013 (last modif: %s). Written in Python 2.7.3 (<u>http://www.python.org<U>).
    The parser of command line arguments is generated with the argparse module.
   By %s,
    ENS de Cachan (M1 Mathematics & M1 Computer Science MPRI).
    
   For Naereen Corp.,
    <u>mailto:naereen-corporation@laposte.net<U>.
    <u>https://sites.google.com/site/naereencorp<U>.""" % (version, date, author)

#: The default description, used when generate a parser by _parser_default function !
_default_description = "WARNING: No description had been given to _parser_default..."

def _add_default_options(parser, version=__version__, date=__date__, author=__author__):
	""" _parser_default(parser, version, date, author) -> argparse.ArgumentParser instance.
	
	Return the parser *parser*, modified by adding default options for the project,
	 which put the options : --version, --verbose, --noANSI and --noUTF
	 and others basic options."""
	parser.add_argument('--version', action='version', version='%(prog)s '+version)
	#################################################
	#: Let those two lines, just to remember that others stuffs.
	parser.add_argument('--noANSI', help="If present, ANSI escape code from ANSIColors are *disable*.", action='store_true', default=False)
	parser.add_argument('--ANSI', help="If present, ANSI escape code from ANSIColors are *forced* to be printed (even if the output is detected to be a pipe).", action='store_true', default=False)
	return parser

# To make a default parser.
def _parser_default(description=_default_description, \
	epilog="WARNING: No extra epilog had been given to _parser_default...", \
	version=__version__, date=__date__, author=__author__, \
	preprocessor = str):
	""" _parser_default(parser, version, date, author) -> argparse.ArgumentParser instance.
	
	Make a new *parser*, initialized by adding default options for the project (with _add_default_options)
	 The default description is *_default_description*,
	 The epilog will *epilog*, then _default_epilog(version, date, author).
	
	preprocessor can be ANSIColors.sprint or __builtin__.str (default value)
	 (*i.e.* a string -> string function),
	 and it will be used as a **preprocessor** for *description* and *epilog* value.
	
	Example:
	 >>> parser = _parser_default(description='<DELETE>A description.',\
		epilog='The description will no begin by the balise DELETE, thanks to sprint preprocessing.',\
 		preprocessor=lambda s: s.replace('<DELETE>', ''))
 	"""
# Passing RawDescriptionHelpFormatter as formatter_class= indicates that description and epilog are already correctly formatted and should not be line-wrapped:
# RawTextHelpFormatter maintains whitespace for all sorts of help text, including argument descriptions.
# The other formatter class available, ArgumentDefaultsHelpFormatter, will add information about the default value of each of the arguments:
	try:
	 import argparse
	 parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,\
		description=preprocessor(description), prefix_chars='-+',\
		epilog=preprocessor(epilog + _default_epilog(version, date, author)))
	# change the function *_add_default_options*, not this one.
	 parser = _add_default_options(parser, version, date, author)
	 return parser
	except ImportError:
	 sys.stderr.write("""ERROR : when I tried to import the 'argparse' module.
 The first possible reason is that you are using a version of Python too old (< 2.7).
 The other possible reason is a other version of Python that the usual CPython :
  * Jython,
  * IronPython,
  * PyPy,
 for instance, are not supported.
""")
	 sys.stderr.flush()
	 sys.exit(1)
################################################################################

ANSISupported = True
try:
	#: If false, the module do almost NOTHING
	ANSISupported='TERM' in os.environ and os.environ['TERM'] != 'unknown'
	if ('--noANSI' in sys.argv) or (not sys.stdout.isatty()): ANSISupported = False
	if '--ANSI' in sys.argv: ANSISupported = True
except Exception as e:
	print "I failed badly when trying to detect if ANSIColors are supported, reason = %s" % e
	ANSISupported = False

# colours bold
black="\033[01;30m"	#: Black and bold.
red="\033[01;31m"	#: Red and bold.
green="\033[01;32m"	#: Green and bold.
yellow="\033[01;33m"	#: Yellow and bold.
blue="\033[01;34m"	#: Blue and bold.
magenta="\033[01;35m"	#: Magenta and bold.
cyan="\033[01;36m"	#: Cyan and bold.
white="\033[01;37m"	#: White and bold.

# colours not bold
Bblack="\033[02;30m"	#: Black and not bold.
Bred="\033[02;31m"	#: Red and not bold.
Bgreen="\033[02;32m"	#: Green and not bold.
Byellow="\033[02;33m"	#: Yellow and not bold.
Bblue="\033[02;34m"	#: Blue and not bold.
Bmagenta="\033[02;35m"	#: Magenta and not bold.
Bcyan="\033[02;36m"	#: Cyan and not bold.
Bwhite="\033[02;37m"	#: White and not bold.

# Background colours : not very usefull
Black="\033[40m"	#: Black background
Red="\033[41m"		#: Red background
Green="\033[42m"	#: Green background
Yellow="\033[43m"	#: Yellow background
Blue="\033[44m"		#: Blue background
Magenta="\033[45m"	#: Magenta background
Cyan="\033[46m"		#: Cyan background
White="\033[47m"	#: White background

# Others : blink and Blink are NOT SUPPORTED BY ALL TERMINAL
blink="\033[05m"	#: Make the text blink. NOT SUPPORTED BY ALL TERMINAL. On Windows (with mintty) it's ok. On Linux (with ttys, gnome-terminal or pyterminal, it's not).
Blink="\033[06m"	#: Make the text not blink (*i.e.* stop blinking).

# nocolors, then default, then Default
nocolors="\033[0m"
default="\033[39m"	#: default foreground
Default="\033[49m"	#: default background

italic="\033[3m"	#: italic
Italic="\033[23m"	#: no italic
b="\033[1m"	#: bold
B="\033[2m"	#: no bold
u="\033[4m"	#: underline
U="\033[24m"	#: no underline
neg="\033[7m"	#: negative
Neg="\033[27m"	#: no negative

# New ones
clear="\033[2J"	#: Clear the screen.
el="\r\033[K"	#: Clear the current line.
reset="\033[0;39;49m"	#: Reset the current foreground and background values to default, and disable all effects.

bell="\007"	#: BEL is the bell character (\007). It *might* be interpreted and a sonor signal might be heard (but not with every terminals).
title="\033]0;"	#: Use it like : writec("<title>.: My title :.<bell>"), **and only** with ending the sequence with <bell>.

# Not specially balises, but aliases.
warning = "%s%s/!\\%s%s" % (red, u, U, default)	#: A well colored Warning symbol (/!\\)

question = "%s%s/?\\%s%s" % (yellow, u, U, default)	#: A well colored question symbol (/?\\)

ERROR = "%s%sERROR%s" % (reset, red, default)	#: A well colored ERROR word.

WARNING = "%s%sWARNING%s" % (reset, yellow, default)	#: A well colored WARNING word.

INFO = "%s%sINFO%s" % (reset, blue, default)	#: A well colored INFO word.

#############################################################
#: List of all authorized colours.
colorList=['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'Bblack', 'Bred', 'Bgreen', 'Byellow', 'Bblue', 'Bmagenta', 'Bcyan', 'Bwhite', 'Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White', 'Blink', 'blink', 'nocolors', 'default', 'Default', 'italic', 'Italic', 'b', 'B', 'u', 'U', 'neg', 'Neg', 'clear', 'el', 'reset', 'bell', 'title', 'warning', 'question', 'ERROR', 'WARNING', 'INFO']
#: List of all simple colours
simpleColorList=['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

# backup all colours
for n in colorList:
 exec('_%s=%s' % (n, n))

# Turn off colour balises interpretation if they are not supported
if not(ANSISupported):
	for n in colorList:
	 exec('%s=\"\"' % n)

def tocolor(string):
	"""tocolor(string) -> string
Convert a string to a colour.
[string] **have** to be in [colorList] to be recognized (and interpreted).
Default value if [string] is not one of the colour name is "" the empty string."""
	if string in colorList:
	 res=""
	 exec('res=%s' % string)
	 return res
	else: return ""

def sprint(chainWithBalises, left='<', right='>', verbose=False):
	""" sprint(chainWithBalises, left='<', right='>', verbose=False) -> string
Parse a string containing colour balises, when colour is one of the previous define name,
and then return it, with colour balises changed to concrete ANSI colour codes.

**Balises are delimited** by [left] and [right].
By default, it's Pango style whit '<' and '>', but you can change them.
For example, a HTML style like : left='<span colour=' and right='>' is also possible. (But, without closing '</span', this is a stupid example. Sorry I didn't find anything else...)

.. warning::

   It is more prudent to put nothing else than ANSI Colors (*i.e.* values in colorList) between '<' and '>' in [chainWithBalises].
   The comportement of the function in case of false balises **is not perfect**.
   Moreover, a good idea could be to don't try to use '<' or '>' for anything else than balises.
   I know, it's not perfect. But, the syntax of color balises is so simple and se beautiful with this limitation that you will surely forgive me this, *won't you* ;) ?
	
Example: ::

    >>> print sprint("<blue>this is blue.<white>And <this> is white.<red>Now this is red because I am <angry> !<green><white>")
    this is blue.And <this> is white.Now this is red because I am <angry> !

*About:*
 This function is used in all the following, so all other function can also used *left* and *right* arguments.
	"""
	ls = chainWithBalises.split(left)
	if verbose:	print "\tls", ls
	lls = list()
	for s2 in ls:
	 if verbose:	 print "\ts2", s2
	 inte=s2.split(right)
	 if verbose:	 print "\tinte", inte
	 if inte[0] in colorList: inte[0]=tocolor(inte[0])
	 else:
	  if len(inte)>1: inte[0]=left+inte[0]+right
	 if verbose:	 print "\tinte", inte
	 lls.append(inte)
	if verbose:	print "\t", lls
	res=""
	for ii in range(len(lls)):
	 for j in range(len(lls[ii])):
	  res+=lls[ii][j]
	return res

def erase(chainWithBalises, left='<', right='>', verbose=False):
	""" erase(chainWithBalises, left='<', right='>', verbose=False) -> string
	Parse a string containing colour balises, when colour is one of the previous define name,
	and then return it, with colour balises **erased**.

	Example:
	 This example seems exactly the same that the previous in the documentation, but it's not (**again**: it is hard and painful (and maybe impossible) to put colour in Sphinx RST files, so there is **no colour in output** in the examples... but be sure there is the real output !).
	  >>> print erase("<blue>This is blue.<white>And <this> is white.<red>Now this is red because I am <angry> !<reset>")
	  This is blue.And <this> is white.Now this is red because I am <angry> !
	"""
	ls = chainWithBalises.split(left)
	if verbose:	print "\tls", ls
	lls = list()
	for s2 in ls:
	 if verbose:	 print "\ts2", s2
	 inte=s2.split(right)
	 if verbose:	 print "\tinte", inte
	 if inte[0] in colorList: inte[0]='' #: Here the 'erasure' is made.
	 else:
	  if len(inte)>1: inte[0]=left+inte[0]+right
	 if verbose:	 print "\tinte", inte
	 lls.append(inte)
	if verbose:	print "\t", lls
	res=""
	for ii in range(len(lls)):
	 for j in range(len(lls[ii])):
	  res+=lls[ii][j]
	return res

def printc(chainWithBalises, left='<', right='>'):
	""" printc(chainWithBalises, left='<', right='>') -> unit
	A shortcut to print sprint(chainWithBalises) : analyse all balises, and print the result."""
	print sprint(chainWithBalises, left=left, right=right)

def writec(chainWithBalises="", file=sys.stdout, left='<', right='>', flush=True):
	""" writec(chainWithBalises="", file=sys.stdout, left='<', right='>', flush=True) -> unit
Usefud to print colored text **to a file**, represented by the object *file*.
Also usefull to print colored text, but without an ending '\\n' caracter.
	
Example:
	
In this example, before the long calcul begin, it print 'Computing 2**(2**(2**4)).....',
and when the computation is done, erase the current line (with <el> balise),
and print ' Done !' in green, and the result of the computation: ::

     >>> writec("<red>Computing<reset> 2**(2**(2**4))....."); tmp=2**(2**(2**4)); writec("<el><green>Done !<reset>")
	 
This example show how to use ANSIColors module to put colored data in a file.
Be aware that this file now contains ANSI escape sequences.
For example, *$ cat /tmp/colored-text.txt * will well print the colours, but editing the file will show *hard values* of escape code (*you know, the stuff that you typically don't want to know anything, the **dirty stuff** !*): ::

    >>> my_file = open('/tmp/colored-text.txt', mode='w') # Open an adhoc file.
    >>> write("<blue>this is blue.<white>And <this> is white.<red>Now this is red because I am <angry> !<green><white>", file=my_file)
	

Remark:
 Can also be used to simply reinitialize the ANSI colors buffer, but the function *Reset* is here for this: ::

    >>> writec("<reset>")


.. warning::
   
   The file *file* **will be flushed** by this function if *flush* is set to True (this is default comportement).
   If you prefer no to, use flush=False option: ::

       >>> writec(chainWithBalises_1), file=my_file, flush=False)
       >>> # many things.
       >>> writec(chainWithBalises_n), file=my_file, flush=False)
       >>> my_file.flush()	# only flush *here*.

"""
	file.write(sprint(chainWithBalises, left=left, right=right))
	if flush: file.flush()

def clearScreen():
	""" clearScreen() -> unit
	Try to clear the screen using ANSI code [clear]."""
	writec("<clear>")

def clearLine():
	""" clearLine() -> unit
	Try to clear the current line using ANSI code [el]."""
	writec("<el>")

def Reset():
	""" Reset() -> unit
	Try to reset the current ANSI codes buffer, using [reset]."""
	writec("<reset>")

####################################
# Other tools for the interface

def notify(msg="", obj=".: Notification sent by ANSIColors.notify :.", icon=None, verb=False):
	 """ notify(msg='', obj='.: Notification sent by ANSIColors.notify :.', icon=None, verb=False) -> bool

Notification using subprocess and notify-send.
Also print the informations directly to the screen (only if verb=True).


.. warning::

   This doesn't use any *ANSI escape* codes, but the common *notify-send* **linux** program.
   It shall fails (but not durty) on Windows or Mac OS X.


Return True iff the title have been correctly changed.
Fails simply if *notify-send* is not found.
	"""
	 try:
	  if icon:
	   subprocess.Popen(['notify-send', obj, msg, "--icon=%s/%s" % (os.getcwd(), icon)])
	   if verb: print "/notify/ A notification have been sent, with obj=%s, msg=%s, and icon=%s." % (obj, msg, icon)
	  else:
	   subprocess.Popen(['notify-send', obj, msg])
	   if verb: print "/notify/ A notification have been sent, with obj=%s, and msg=%s." % (obj, msg)
	  return 0
	 except Exception as e:
	  if verb: print "/notify/ notify-send : not-found ! Returned exception is %s." % e
	  return -1

def xtitle(new_title="", verb=False):
	 """ xtitle(new_title="", verb=False) -> 0|1
**Modify the current terminal title**.
Returns 0 if one of the two solutions worked, 1 otherwise.
 
An experimental try is with **ANSI escape code**,
if the simple way by *invoking* the **xtitle** program doesn't work (or if it is not installed).

.. note::

   The second solution used the two *ANSI* Balises <title> and <bell>.
   So, you can also do it with : ::
   
       >>> ANSIColors.writec("<title>.: This is the new title of the terminal :.<bell>")

   
But this function *xtitle* is better : it tries two ways, and returns a signal to inform about his success.
"""
	 try:
	  subprocess.Popen(['xtitle', new_title])
	  if verb: print "/xtitle/ The title of the current terminal has been set to '%s'." % new_title
	  return 0
	 except Exception as e:
	  if verb: print "/xtitle/ xtitle : not-found ! Returned exception is %s." % e
	  try:
	   writec("<title>%s<bell>" % new_title)
	  except Exception as e:
	   if verb: print "/xtitle/ With ANSI escape code <title> and <bell> : failed. ! Returned exception is %s." % e
	   return 2
	  return 0

########################
##### Script part ######
########################

# To generate ~/.color.sh with this script, 
# use ./ANSIColors.py -g,
def _Generate_color_sh(file_name=None):
	""" _Generate_color_sh(file_name=None) -> string | unit.
	Used to print or generate (if file_name is present and is a valid URI address)
	 a profile of all the colours *here* defined.
	
	Print all ANSI Colors as 'export name=value'.
	 Usefull to auto generate a ~/.color.sh to be used with Bash,
	 use the command './ANSIColors.sh --generate --file ~/.color.sh',
	 and now you can simply colorized your Bash script with '. ~/.color.sh' to import all colours.

	The file is a list of 'export NAME="VALUE"', to be used with GNU Bash.
	"""
	from time import sleep
	if file_name:
	 writec("<green> The file %s is creating.<reset> (c) Naereen CORP. 2013.\t" % file_name)
	writec("<blue><u>Listing of all ANSI Colors...<reset>")
	sleep(0.9)
	writec("<el>...")
	for s in colorList:
		writec("<green><u>%s<reset>..." % s)
		sleep(0.1)
		writec("<el>...")
	writec("<reset>Listing of all ANSI Colors...><red><u> DONE !<reset>...")
	sleep(0.9)
	writec("<el>")
	if file_name:
	 mfile=open(file_name, 'w')
	else:
	 mfile=sys.stdout
	mfile.write("""#!/bin/sh
# From ANSIColors.py module, auto generated with -g option. (*i.e.* the command './ANSIColors.py --generate')
#About the convention for the names of the colours :
# * for the eight colours black, red, green, yellow, blue, magenta, cyan, white:
#  * the name in minuscule is for colour **with bold** (example 'yellow'),
#  * the name starting with 'B' is for colour **without bold** (example 'Byellow'),
#  * the name starting with a capital letter is for the background colour (example 'Yellow').
# * for the special effects (blink, italic, bold, underline, negative), **not always supported** :
#  * the name in minuscule is for **activate** the effect,
#  * the name starting in capital letter is for **desactivate** the effect.
# * for the other special effects (nocolors, default, Default, clear, el), the effect is **immediate** (and seems to be well supported).

#About:
#======
#	Use this script with other GNU Bash scripts, simply by importing him with
#	 $ . ~/.color.sh

#Copyrigths:
#===========
#   (c) 01/2013
#   By Lilian BESSON,
#    ENS de Cachan (M1 Mathematics & M1 Computer Science MPRI)
#    mailto:lbesson@ens-cachan.fr
#    
#   For Naereen Corp.
#    mailto:naereen-corporation@laposte.net
#    https:sites.google.com/site/naereencorp
#
#List of colors:
#===============
""")
	res = ""
	for s in colorList:
	  exec("res=('%%s' %% %s)" % s.replace('\x1b', '\\\\x1b'))
	  #: Un excaping special caracters.
	  res=res.replace('\x1b', '\\033')
	  res=res.replace('\r', '\\r')
	  mfile.write("export %s=\"%s\"\n" % (s, (r"%s" % res)))
	mfile.write("#DONE\n\n")
	if file_name:
	 writec("<green> The file %s have been creating.<reset> (c) Naereen CORP. 2013.\n" % file_name)
	 sys.exit(0)

def _run_complete_tests(color_list_tested=colorList):
	""" _run_complete_tests(color_list_tested=colorList) -> unit.
	Launch a complete test of all ANSI Colors code in the list *color_list_tested*.
	"""
	printc("Launching full test for ANSI Colors.<default><Default><nocolors> now the text is printed with default value of the terminal...")
	for s in color_list_tested:
	 printc("The colour '%s'\t is used to make the following effect : <%s>!! This is a sample text for '%s' !!<default><Default><nocolors>..." % (s, s, s))

###############
##### End #####

if __name__ == '__main__':
	#: Generate the parser, with another module.
	#: This variable is the preprocessor, given to description and epilog by ParseCommandArgs,
	#:  * erase: to print with no colours.
	#:  * sprint: to print with colours.
	preprocessor = sprint if ANSISupported else erase 	#:preprocessor = __builtin__.str, if you wanna to *see* the balises.
	#: Generate the parser, with another module.
	parser = _parser_default(\
		description='<green>ANSI Colors utility <red>module<reset> and <blue>script<reset>.',\
		epilog="""\n\
<yellow>About:
======<reset>
 This module is <blue>still in development<reset>.
 Last version of this project can be found <green>on-line<reset> :
  * here on <neg>BitBucket<Neg> : <u>https://bitbucket.org/lbesson/ansi-colors<U>,
  * here on <neg>PyPi<Neg> : <u>https://pypi.python.org/pypi/ANSIColors-balises<U>,
  * and his documentation can be found here on <neg>Python Hosted<Neg> : <u>http://pythonhosted.org/ANSIColors-balises/<U>.
 
 The reference page for ANSI code is : <u>http://en.wikipedia.org/wiki/ANSI_escape_code<U>.""", \
		version=__version__, date=__date__, author=__author__, \
 		preprocessor=preprocessor)
	#: So, here become the intersting part.
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-t","--test", help="Launch a complete test of all ANSI Colors code defined here.", action="store_true")
	#: Description for the part with '--file' and '--generate' options.
	group = parser.add_argument_group('Generation of a GNU Bash colour aliases file', preprocessor("""\
<b>About the <u>convention<U> for the names of the colours :<reset>
 * for the eight colours black, red, green, yellow, blue, magenta, cyan, white:
  * the name in minuscule is for colour **with bold** (example <yellow>'yellow'<reset>),
  * the name starting with 'B' is for colour **without bold** (example <Byellow>'Byellow'<reset>),
  * the name starting with a capital letter is for the background colour (example <Yellow>'Yellow'<reset>);
 * for the special effects (blink, italic (i), bold (b), underline (u), negative), <u>**not always supported**<reset> :
  * the name in minuscule is for <u>**activate**<reset> the effect (example 'u' to <u>underline<U>),
  * the name starting in capital letter is for <u>**desactivate**<reset> the effect (example 'U' to stop underline);
 * for the other special effects (nocolors, default, Default, clear, el), the effect is <u>**immediate**<reset> (and seems to be well supported).

Use this script with other GNU Bash scripts, simply by importing him with
<b><black> . ~/.color.sh<reset>"""))
	group.add_argument("-g","--generate", help="Print all ANSI Colors as 'export name=value'.", action="store_true") #:, required=True)
	group.add_argument("-f","--file", help="If present, and with --generate option, don't print the values, but export them in the file FILE.", default=None)
	#: The parser is done,
	#: Use it to extract the args from the command line.
	args = parser.parse_args()
	#: Use those args.
	if args.generate:
	 if args.file:
	  _Generate_color_sh(args.file)
	 else:
	  _Generate_color_sh()
	 sys.exit(0)
	if args.test:
	 _run_complete_tests()
	 sys.exit(0)
	parser.print_help()
	sys.exit(1)
##############################################################################
# remove the scripts values here
# FIXME: be sure we removed exactly the good ones
else:
	del(_Generate_color_sh)
	del(_run_complete_tests)
	del(_parser_default)
	del(_default_description)
	del(_default_epilog)
	del(_add_default_options)