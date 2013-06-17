#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/rpmgetopts.py,v 1.3 2009/11/25 07:55:36 csoftmgr Exp $
# $Date: 2009/11/25 07:55:36 $

import Csys, os, os.path, sys, re

__doc__ = '''Get rpm options for OpenPKG builds

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: rpmgetopts.py,v 1.3 2009/11/25 07:55:36 csoftmgr Exp $
'''

__version__='$Revision: 1.3 $'[11:-2]

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

	parser.add_option('-b', '--binrpm',
		action='store_true', dest='binrpm', default=False,
		help='Use /bin/rpm',
	)
	parser.add_option('-d', '--defines',
		action='store_true', dest='defines', default=False,
		help='Generate --defines for build',
	)
	parser.add_option('-f', '--filename',
		action='store', dest='filename', default='',
		help='Append to filename deleting -D lines',
	)
	return parser
#} setOptions

parser = setOptions()

(options, args) = parser.parse_args()

verbose = ''
if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

if options.binrpm:	rpmcmd = '/bin/rpm'
else:				rpmcmd = Csys.Config.rpm

if not args: #{
	fh = Csys.popen("%s -qa --qf='%%{NAME}\n'" % rpmcmd)
	args = [line.rstrip() for line in fh]
	fh.close()
	args.sort()
#}
outlines = []

fmt = '-D %(rpm)s::%(module)s=%(state)s'
if options.defines: #{
	fmt = "\t--define '%(module)s %(state)s' \\"
#}
if verbose: sys.stderr.write('%s\n' % (fmt))

class Rpm(object): #{
	def __init__(self, rpm): self.rpm = rpm
#}

for rpm in args: #{
	pkg = Rpm(rpm)
	fh = Csys.popen('%s -qi %s' % (rpmcmd, rpm))
	found_provides = False
	if verbose: sys.stderr.write('checking %s...\n' % rpm)
	pattern = re.compile(r'\s+%s::(\S+) = (.*)' % rpm)
	for line in fh: #{
		if not (found_provides or line.startswith('Provides')): continue
		found_provides = True
		R = pattern.search(line)
		if R: #{
			pkg.module, pkg.state = R.groups()
			outlines.append(fmt % pkg.__dict__)
		#}
	#}
	if options.defines: #{
		outlines.sort()
		outlines.insert(0, 'openpkg rpm "$@" \\' )
		outlines.append('\t%s.spec' % rpm)
		break
	#}
#}
if not options.defines: outlines.sort()

if options.filename: #{
	fh = open(options.filename)
	for line in fh: #{
		if not line.startswith('-D '): print line[:-1]
	#}
#}
print '\n'.join(outlines)
