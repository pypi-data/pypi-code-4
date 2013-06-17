#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/termcapcmp.py,v 1.1 2011/10/05 19:30:44 csoftmgr Exp $
# $Date: 2011/10/05 19:30:44 $

import Csys, os, os.path, sys, re

import Csys.Termcap

__doc__ = '''Termcap extract and comparison

usage: %s term file1 [file2 ...]''' % Csys.Config.progname

__doc__ += '''

$Id: termcapcmp.py,v 1.1 2011/10/05 19:30:44 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

# taken directly from the csbase ctc.c program.

try: #{{
	termcapRawMap = Csys.Termcap.termcapRawMap
	termcapMap = Csys.Termcap.termcapMap
#}
except AttributeError: #{
	termcapRawMap = [
		("ae", "end alternate character set"         ),
		("al", "add (insert) blank line"             ),
		("AL", "Multiplan sent by ALTERNATE Key"),
		("am", "automatic margins"                   ),
		("as", "start alternate character set"       ),
		("bc", "backspace if not ^H"),
		("BE", "Multiplan Bell Character"),
		("Bj", "bottom join graphic"                 ),
		("bl", "bell"                                ),
		("Bl", "bottom left corner graphic"          ),
		("Br", "bottom right graphic"                ),
		("bs", "^h does backspace"                   ),
		("BS", "Multiplan BACKSPACE (not ^h)"),
		("bt", "back tab"                            ),
		("bw", "backspace wraps backwards"           ),
		("C0", "Printer, Correspondance 16 Pitch"),
		("CA", "Printer, Correspondance 10 Pitch"),
		("CC", "command character in prototype"      ),
		("cd", "clear to end of display"             ),
		("ce", "clear to end of line"                ),
		("CF", "Tandy Xenix: Cursor Off"),
		("cf", "UNIFY clear unprotected fields"),
		("ch", "like cm but horizontal motion only"  ),
		("Cj", "center join (cross) graphic"         ),
		("cl", "clear screen"                        ),
		("CL", "Tandy Xenix: sent by CHAR LEFT key"  ),
		("cm", "cursor motion"                       ),
		("CN", "Multiplan sent by CANCEL key"),
		("co", "number of columns in a line"         ),
		("CO", "Tandy Xenix: Cursor On"),
		("cr", "carriage return"                     ),
		("CR", "Multiplan sent by CHARACTER RIGHT"),
		("cs", "change scrolling region (vt100)"     ),
		("ct", "clear tabs"                          ),
		("CU", "Multiplan Shell Escape"),
		("cv", "like ch but vertical only"           ),
		("CW", "Xenix Change Window Key"),
		("da", "display may be retained above"       ),
		("DA", "Xenix Delete Attribute (bool)"),
		("db", "display may be retained below"       ),
		("dB", "number of millisec of bs delay"      ),
		("dc", "delete character"                    ),
		("dC", "number of millisec of cr delay"      ),
		("dF", "number of millisec of ff delay"      ),
		("DK", "Multiplan sent by DOWN ARROW"),
		("dl", "delete line"                         ),
		("DL", "Multiplan sent by DELETE key"),
		("dm", "enter delete mode"                   ),
		("dN", "number of millisec of nl delay"      ),
		("dn", "down one line?"      ),
		("do", "down one line"                       ),
		("ds", "erase status line"                   ),
		("dT", "number of millisec of tab delay"     ),
		("ec", "erase character"                     ),
		("Ec", "UNIFY ENTER Clear Entry ^Z"),
		("ed", "end delete mode"                     ),
		("ei", "end insert mode"                     ),
		("EM", "Multiplan sent by EDIT MACRO Key"),
		("EN", "Xenix Sent by END Key"),
		("eo", "can erase overstrikes with a blank"  ),
		("es", "escape ok on status line"            ),
		("Es", "UNIFY ENTER Begin Search ^E"),
		("EX", "Multiplan sent by EXTEND SELECT key"),
		("Ex", "UNIFY ENTER Exit ^X"),
		("ff", "hardcopy terminal page eject"        ),
		("fs", "end status line, restore cursor"     ),
		("G1", "Xenix Upper-Right Corner Character"),
		("G2", "Xenix Upper-Left Corner Character"),
		("G3", "Xenix Lower-Left Corner Character"),
		("G4", "Xenix Lower-Right Corner Character"),
		("ga", "UNIFY Lower left round corner"),
		("gb", "UNIFY Upper left round corner"),
		("gc", "UNIFY Upper right round corder"),
		("GC", "Xenix Center Graphics (+) Character"),
		("gd", "UNIFY Lower right round corner"),
		("GD", "Xenix Down Tick Character"),
		("Ge", "enter graphics mode"                 ),
		("ge", "UNIFY Lower left square corner"),
		("GE", "Xenix Graphics Mode End"),
		("gf", "UNIFY Upper left square corner"),
		("gg", "UNIFY Upper right square corner"),
		("GG", "Xenix Number of Chars for GS & GE"),
		("gh", "UNIFY Lower right square corner"),
		("GH", "Xenix Horizontal bar Character"),
		("gi", "UNIFY + intersection"),
		("gj", "UNIFY vertical bar"),
		("gk", "UNIFY Horizontal bar"),
		("gl", "UNIFY --| intersection"),
		("GL", "Xenix Left Tick Character"),
		("gm", "UNIFY |-- intersection"),
		("gn", "generic line type (eg, dialup)"      ),
		("gn", "UNIFY T intersection"),
		("go", "UNIFY _|_ intersection"),
		("GR", "Xenix Right Tick Character"),
		("Gs", "start graphics mode"                 ),
		("gs", "UNIFY start graphics mode"),
		("GS", "Xenix Graphics Mode Start"),
		("GU", "Xenix Up-Tick Character"),
		("GV", "Xenix Vertical Bar Character"),
		("gx", "UNIFY exit graphics mode"),
		("GZ", "FILEPRO-16 field end mark Character"),
		("hc", "hardcopy terminal"                   ),
		("hd", "forward 1/2 linefeed"                ),
		("Hl", "horizontal line graphic"             ),
		("HM", "Multiplan Home (if not kh)"),
		("ho", "home cursor (if not cm)"),
		("HP", "Multiplan Sent by Help Key"),	
		("hs", "status line"                         ),
		("hu", "reverse 1/2 linefeed"                ),
		("HW", "Multiplan sent by HOME WINDOW key"),
		("hz", "hazeltine; can't print ~'s"          ),
		("ic", "insert character"                    ),
		("if", "name of file containing is"          ),
		("im", "insert mode (enter)"                 ),
		("in", "enter insert mode"                   ),
		("ip", "insert pad after character inserted" ),
		("is", "terminal initialization string"      ),
		("it", "initial tabs every n spaces"         ),
		("k;", "sent by other function key 10"       ),
		("k0", "sent by other function key 0"        ),
		("k1", "sent by other function key 1"        ),
		("k2", "sent by other function key 2"        ),
		("k3", "sent by other function key 3"        ),
		("k4", "sent by other function key 4"        ),
		("k5", "sent by other function key 5"        ),
		("k6", "sent by other function key 6"        ),
		("k7", "sent by other function key 7"        ),
		("k8", "sent by other function key 8"        ),
		("k9", "sent by other function key 9"        ),
		("ka", "sent by clear-all-tabs key"          ),
		("kA", "sent by insert-line key"             ),
		("kb", "sent by backspace key"               ),
		("kB", "sent by reverse-tab key"             ),
		("kC", "sent by clear key"                   ),
		("kD", "sent by delete-character key"        ),
		("ku", "sent by terminal up arrow key"       ),
		("kd", "sent by terminal down arrow key"     ),
		("kl", "sent by terminal left arrow key"     ),
		("kr", "sent by terminal right arrow key"    ),
		("ke", "out of keypad-transmit mode"         ),
		("kE", "sent by clear-to-eol key"            ),
		("kF", "sent by scroll-forward/down key"     ),
		("kH", "sent by home key"                    ),
		("kh", "sent by home key"                    ),
		("kI", "sent by ins-char/enter-ins-mode key" ),
		("kL", "sent by delete-line key"             ),
		("km", "has meta-shift key"                  ),
		("kM", "sent by rmir or smir in insert mode" ),
		("kn", "number of other keys"                ),
		("kN", "sent by next-page key"               ),
		("kP", "sent by previous-page key"           ),
		("kR", "sent by scroll-backward/up key"      ),
		("ks", "put terminl in keypad-transmit mode" ),
		("kS", "sent by clear-to-end-of-screen key"  ),
		("kt", "sent by clear-tab key"               ),
		("kT", "sent by set-tab key"                 ),
		("L0", "FILEPRO-16 insc Insert Character"),
		("l0", "label on function key 0"             ),
		("L1", "FILEPRO-16 delc Delete Character"),
		("l1", "label on function key 1"             ),
		("L2", "FILEPRO-16 insl Insert Line"),
		("l2", "label on function key 2"             ),
		("L3", "FILEPRO-16 dell Delete Line"),
		("l3", "label on function key 3"             ),
		("L4", "FILEPRO-16 save record [ESC] [ESC]"),
		("l4", "label on function key 4"             ),
		("L5", "FILEPRO-16 dupl Duplicate Key"),
		("l5", "label on function key 5"             ),
		("L6", "FILEPRO-16 utab Up Tab"),
		("l6", "label on function key 6"             ),
		("L7", "FILEPRO-16 dtab Down Tab"),
		("l7", "label on function key 7"             ),
		("L8", "FILEPRO-16 ltab Left Tab"),
		("l8", "label on function key 8"             ),
		("L9", "FILEPRO-16 rtab Right Tab"),
		("l9", "label on function key 9"             ),
		("LA", "FILEPRO-16 clef Clear End of Field"),
		("la", "label on function key 10"            ),
		("LB", "FILEPRO-16 dmap Display Fields"),
		("LC", "FILEPRO-16 Redraw,Multiplan PREVULK"),
		("LD", "FILEPRO-16 Enter Print Code Label"),
		("Ld", "FILEPRO-16 prtc Enter Print Codes"),
		("le", "cursor left"                         ),
		("LE", "FILEPRO-16 dprt Display Print Codes"),
		("LF", "FILEPRO-16 Restore Cursor,MP Prevfld"),
		("LG", "FILEPRO-16 crup Up Arrow (DT-1)"),
		("LH", "FILEPRO-16 cdwn Down Arrow (DT-1)"),
		("LI", "FILEPRO-16 clft Left Arrow (DT-1)"),
		("li", "number of lines on screen or page"   ),
		("LJ", "FILEPRO-16 crgt Right Arrow (DT-1)"),
		("Lj", "left join graphic"                   ),
		("LK", "FILEPRO-16 home (DT-1)"),
		("LK", "Multiplan Left Arrow (if not kl)"),
		("ll", "last line, first column"             ),
		("LM", "FILEPRO-16 bkps Break Pause (DT-100)"),
		("LY", "FILEPRO-16 Cancel Key Label"),
		("LZ", "FILEPRO-16 Carriage Return Key Label"),
		("lm", "lines of memory"                     ),
		("LO", "FILEPRO-16 Help"),
		("ma", "arrow key map (vi version 2 only)"   ),
		("mb", "enter blink enhance"                 ),
		("md", "enter bold mode"                     ),
		("me", "exit attribute mode (normal mode)"   ),
		("mh", "enter dim enhance"                   ),
		("mi", "safe to move while in insert mode"   ),
		("mk", "enter blank enhance"                 ),
		("ml", "memory lock on above cursor"         ),
		("mm", "metachar mode on"                    ),
		("mo", "metachar mode off"                   ),
		("mp", "enter protect mode"                  ),
		("MP", "Multiplan Initialization String"),
		("mr", "enter reverse enhance"               ),
		("MR", "Multiplan Reset String"),
		("ms", "safe to move while in so and ul mode"  ),
		("mu", "memory unlock (turnoff memory lock)" ),
		("nc", "no correctly working carriage retrn" ),
		("nd", "nondestructive space (cursor right)" ),
		("nl", "newline character"                   ),
		("NM", "Multiplan Normal Video"),
		("nm", "UNIFY Begin normal video mode"),
		("NR", "Multiplan Reverse Video"),
		("ns", "terminal is CRT but doesn't scroll"  ),
		("NU", "Multiplan Next Unlocked Cell"),
		("nw", "new-line carriage-return"            ),
		("os", "terminal overstrikes"                ),
		("P0", "FILEPRO-16 insc Insert Character"),
		("p0", "turn on printer"                     ),
		("P1", "FILEPRO-16 delc Delete Character"),
		("P2", "FILEPRO-16 insl Insert Line"),
		("P3", "FILEPRO-16 dell Delete Line"),
		("P4", "FILEPRO-16 save record [ESC] [ESC]"),
		("P5", "FILEPRO-16 dupl Duplicate Key"),
		("P6", "FILEPRO-16 utab Up Tab"),
		("P7", "FILEPRO-16 dtab Down Tab"),
		("P8", "FILEPRO-16 ltab Left Tab"),
		("P9", "FILEPRO-16 rtab Right Tab"),
		("PA", "FILEPRO-16 clef Clear End of Field"),
		("PB", "FILEPRO-16 dmap Display Fields"),
		("pb", "lowest baud rate requiring padding"  ),
		("PC", "FILEPRO-16 Redraw,Multiplan PREVULK"),
		("pc", "pad character (rather than null)"    ),
		("Pd", "FILEPRO-16 prtc Enter Print Codes"),
		("PD", "Multiplan sent by PAGE DOWN key"),
		("PE", "FILEPRO-16 dprt Display Print Codes"),
		("pe", "UNIFY End Protect Mode"),
		("PF", "FILEPRO-16 Restore Cursor,MP Prevfld"),
		("pf", "turn off the printer"                ),
		("PG", "FILEPRO-16 crup Up Arrow (DT-1)"),
		("PH", "FILEPRO-16 cdwn Down Arrow (DT-1)"),
		("PI", "FILEPRO-16 clft Left Arrow (DT-1)"),
		("PJ", "FILEPRO-16 crgt Right Arrow (DT-1)"),
		("PK", "FILEPRO-16 home (DT-1)"),
		("PL", "Multiplan sent by PAGE LEFT key"),
		("PM", "FILEPRO-16 bkps Break Pause (DT-100)"),
		("PN", "Tandy Xenix: enable printer port"),
		("PO", "FILEPRO-16 Help"),
		("po", "turn on the printer"                 ),
		("PR", "Multiplan sent by PAGE RIGHT key"),
		("PS", "Tandy Xenix: disable printer port"),
		("ps", "UNIFY Start Protect, print screen"   ),
		("pt", "has hardware tabs"                   ),
		("PP", "csysvlp PostScript Printer Type"),
		("PU", "Multiplan sent by PAGE UP key"),
		("PW", "Multiplan sent by PREV WINDOW Key"),
		("RC", "Multiplan Sent by RECALC Key"),
		("rc", "restore cursor to positn of last sc" ),
		("RD", "Multiplan Redraw Screen"),
		("re", "UNIFY End Reverse Underline"),
		("rf", "file containing reset string"        ),
		("RF", "Multiplan sent by TOGGLE REF Key"),
		("rg", "UNIFY Reverse glitch"),
		("Rj", "right join graphic"                  ),
		("RK", "Multiplan sent by RIGHT ARROW key"),
		("rl", "UNIFY Begin Reverse Low"),
		("rP", "like ip but when in replace mode"    ),
		("RT", "Multiplan sent by RETURN Key"),
		("ru", "UNIFY End Reverse Low"),
		("rv", "UNIFY Start Reverse Underline"),
		("rw", "UNIFY Begin Reverse Underline Low"),
		("S0", "Printer, Standard 16 Pitch"),
		("SA", "Printer, Standard 10 Pitch"),
		("SC", "Printer, Standard 12 Pitch"),
		("sc", "save cursor position"                ),
		("se", "end stand out mode"                  ),
		("sf", "scroll forwards"                     ),
		("sg", "number of blank chars left by so"    ),
		("so", "begin stand out mode"                ),
		("sr", "scroll reverse (backwards)"          ),
		("ST", "Multiplan sent by SINGLE STEP key"),
		("st", "set a tab in current column"         ),
		("ta", "tab"                                 ),
		("T1", "csysvlp input tray 1"),
		("T2", "csysvlp input tray 2"),
		("TB", "Multiplan sent by TAB key"),
		("tc", "goto terminal - must be last"        ),
		("te", "string to end programs that use cm"  ),
		("ti", "string to begin progs that use cm"   ),
		("Tj", "top join graphic"                    ),
		("Tl", "top left corner graphic"             ),
		("Tr", "top right corner graphic"            ),
		("ts", "enter status line entry mode"        ),
		("Ub", "UNIFY ENTER move back/up ^U"),
		("uc", "underscore one char and move past"   ),
		("ue", "end underscore mode"                 ),
		("Uf", "UNIFY ENTER move forward/down"),
		("ug", "number of blank chars left by us"    ),
		("Ui", "UNIFY ENTER help current field ^I"),
		("UK", "Multiplan sent by UP ARROW key"),
		("ul", "underlines, doesn't overstrike"      ),
		("UP", "Sent by Up-Arrow (alt to ku)"),
		("up", "upline (cursor up)"                  ),
		("us", "start underscore mode"               ),
		("vb", "visible bell (may not move cursor)"  ),
		("ve", "sequence to end open/visual mode"    ),
		("vi", "put terminal in visual mode"         ),
		("Vl", "vertical line graphic"               ),
		("vs", "sequence to start open/visual mode"  ),
		("we", "UNIFY End Write Protect"),
		("WL", "Multiplan sent by WORD LEFT Key"),
		("WR", "Multiplan sent by WORD RIGHT Key"),
		("ws", "UNIFY Start Write Protect"),
		("xb", "beehive (f1=escape, f2=ctrl C)"      ),
		("Xc", "other special graphic"               ),
		("xn", "newline ignord after wrap (Concept)" ),
		("xo", "terminal uses xon/xoff flow ctrl"    ),
		("xr", "return acts like \r\n (DeltaData)"   ),
		("xs", "standout not erased by overwrite"    ),
		("xt", "tabs destroy, magic so(Teleray1061)" ),
		("xv", "vt100 col 80 glitch"                 ),
	]; # termcapRawMap

	termcapMap = Csys.CSClassDict(dict([tc for tc in termcapRawMap]))
#}}

def main(): #{
	termcapMapFields = set(termcapMap.__dict__.keys())
	# Add program options to parser here

	def setOptions(): #{
		'''Set command line options'''
		global __doc__

		parser = Csys.getopts(__doc__)

	#	parser.add_option('-d', '--directory',
	#		action='store', type='string', dest='directory', default=None,
	#		help='Change to directory before starting process',
	#	)
		parser.add_option('-a', '--all',
			action='store_true', dest='all', default=False,
			help='Print all entries including undefined',
		)
		parser.add_option('-d', '--diffs',
			action='store_true', dest='diffs', default=False,
			help='Print only differences',
		)
		parser.add_option('-n', '--nopadremove',
			action='store_true', dest='nopadremove', default=False,
			help='Do not remove padding',
		)
		parser.add_option('-t', '--terms',
			action='store_true', dest='terms', default=False,
			help='Compare terminal entries in same termcap',
		)
		parser.add_option('-x', '--xml',
			action='store_true', dest='xml', default=False,
			help='Generate DocBool XML table output',
		)
		return parser
	#} setOptions

	parser = setOptions()

	(options, args) = parser.parse_args()

	verbose = ''
	if options.verbose: #{
		verbose = '-v'
		sys.stdout = sys.stderr
	#}
	Csys.getoptionsEnvironment(options)
	# term = args and args.pop(0) or os.environ['TERM']
	if options.terms: #{{
		try: #{{
			termcaps = [args[0]]
			terms = args[1:]
		#}
		except IndexError, e: #{
			print (
				'Usage %s -t termcap term1 term2 ...'
			) % Csys.Config.progname
			sys.exit(1)
		#}}
	#}
	else: #{
		terms = [args.pop(0)]
		termcaps = [args]
	#}}
	if verbose: #{
		print 'terms: ', terms
		print 'termcaps: ', termcaps
	#}
	all = options.all
	compareTermcaps = []
	pattern = r'^\d+\\E'
	noPaddingRemove = options.nopadremove
	if not noPaddingRemove: #{
		paddingPattern = re.compile(pattern)
		paddingReplace = r'\\E'
	#}
	fieldPattern = re.compile(r'^([^=]{1,2}).*')
	for termcap in termcaps: #{
		fmts = ['%-2s']
		fieldNames = set([])
		for term in terms: #{
			l = len(termcap)
			tc = Csys.Termcap.getTermcap(term, termcap, False)
			fields = [f for f in tc.entries.split(':') if f.strip()]
			fieldNames |= set([fieldPattern.sub(r'\1', f) for f in fields[1:]])
			unknownFields = fieldNames - termcapMapFields
			for field in unknownFields: #{
				termcapRawMap.append((field, 'unknown'))
				termcapMapFields |= unknownFields
			#}
			compareTermcaps.append(tc)
			cols = tc.__dict__
			for key, desc in termcapRawMap: #{
				if key in cols: #{
					try: #{{
						val = str(cols.get(key, ''))
						if not noPaddingRemove: #{
							val = paddingPattern.sub(paddingReplace, val)
						#}
						cols[key] = val
						l = max(l, len(cols.get(key, '')))
					#}
					except TypeError: #{
						pass
					#}}
				#}
			#}
			fmts.append('%%-%ds' % l)
		#}
		xml = options.xml
		if not xml: #{{
			fmts.append('%s')
			fmt = ' '.join(fmts)
			l = tuple([''] + [tc.fname for tc in compareTermcaps] + [''])
			print fmt % l
			l = tuple(['CD'] + [tc.term for tc in compareTermcaps] + ['Description'])
			print  fmt % l
		#}
		else: #{
			print '<!--[--><informaltable>'
			n = len(compareTermcaps) + 2
			print '\t<tgroup cols="%d" align="left" colsep="0" rowsep="0">' % n
			for i in range(1, n + 1): #{
				print '\t<colspec colname="c%d"/>' % i
			#}
			print '\t<spanspec spanname="hdrspan" namest="c1" nameend="c%d" align="left"/>' % n
			print '\t<thead><row>'
			for tc in compareTermcaps: #{
				if tc.fname: print '\t\t<entry align="LEFT">%s</entry>' % tc.fname
			#}
			print '\t\t<entry>CD</entry>'
			for tc in compareTermcaps: #{
				print '\t\t<entry align="left">%s</entry>' % tc.term
			#}
			print '\t\t<entry align="left">Description</entry>'
			print '\t</row></thead>'
			print '\t<!--[--><tbody>'
		#}}
		for key, desc in termcapRawMap: #{
			vals = [key]
			hasval = False
			for termcap in compareTermcaps: #{
				cols = termcap.__dict__
				if key in cols: #{
					hasval = True
				#}
				val = cols.get(key)
				vals.append(str(val))
			#}
			if all or hasval: #{
				printit = True
				if options.diffs and len(vals) > 2: #{
					val = vals[1]
					for i in range(2, len(vals)): #{{
						if val != vals[i]: break
					#}
					else: #{
						printit = False
					#}}
				#}
				if printit: #{
					vals.append(desc)
					if not xml: #{{
						print fmt % tuple(vals)
					#}
					else: #{
						print '\t<row>'
						for val in vals: #{
							print '\t\t<entry>%s</entry>' % val
						#}
						print '\t</row>'
					#}}
				#}
			#}
		#}
		if xml: #{
			print '\t</tbody></tgroup><!--]-->'
			print '</informaltable><!--]-->'
		#}
	#}
#}
if __name__ == '__main__': #{
	main()
#}
