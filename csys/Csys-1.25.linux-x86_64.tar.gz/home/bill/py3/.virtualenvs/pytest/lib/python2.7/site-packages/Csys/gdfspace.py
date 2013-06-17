#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/gdfspace.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
# $Date: 2009/11/25 01:44:53 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: gdfspace.py,v 1.1 2009/11/25 01:44:53 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

#	parser.add_option('-d', '--directory',
#		action='store', type='string', dest='directory', default=None,
#		help='Change to directory before starting process',
#	)
#	parser.add_option('-r', '--restart',
#		action='store_true', dest='restart', default=False,
#		help='restart without raising mailbox flags intially',
#	)
	return parser
#} setOptions

parser = setOptions()

(options, args) = parser.parse_args()

if options.verbose: verbose = '-v'
else: verbose = ''

Csys.getoptionsEnvironment(options)

if not args: #{
	from Csys.SysUtils import getMounted
	for dir, d in getMounted().items(): #{
		if not (d.pseudo or d.tmpfs): args.append(d.dir)
	#}
	args.sort()
#}
# Csys.run('mount')
# print args; sys.exit(0)

Blksize	= 1024;
Mbyte	= 1048576.00;
CONST	= Blksize / Mbyte;

cmd = ('gdf -P %s 2>/dev/null' % ' '.join(args))
if verbose: sys.stderr.write('%s\n' % cmd)

df = Csys.popen(cmd)
df.readline() # skip first line

Cumfree = Cumalloc = 0

for line in df: #{
	line = line.strip()
	(filesys, alloc, tmpalloc, free, cap, dir) = line.split();
	alloc		= int(alloc)
	tmpalloc	= int(tmpalloc)
	free		= int(free)
	tfree	= max(0, (free * CONST) - .005)	# force rounding down.
	talloc	= max(0, (alloc * CONST) - .005)	# force rounding down.
	try: #{{
		pct	= free * 100 / alloc;
	#}
	except ZeroDivisionError: #{
		print line
		raise
	#}}
	print ('%-10s: Disk space: %#6.2f MB of %#7.2f MB available (%#5.2f%%)'
		% ( dir, tfree, talloc, pct ));
	Cumfree += free; Cumalloc += alloc;
#}
if (Cumalloc != 0): #{
	CumPct		= Cumfree * 100 / Cumalloc;
	Cumfree		= ( Cumfree * CONST) - .005;	# force rounding down.
	Cumalloc	= ( Cumalloc * CONST) - .005;	# force rounding down.
	print ("\nTotal Free Space: %#6.2f MB Used %#6.2f MB of %#6.2f MB available (%#5.2f%%)"
	% (Cumfree, Cumalloc - Cumfree, Cumalloc, CumPct)
	);
#}
