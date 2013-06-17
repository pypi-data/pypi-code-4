#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/putty2sshpub.py,v 1.2 2009/11/25 07:52:38 csoftmgr Exp $
# $Date: 2009/11/25 07:52:38 $

import Csys, os, os.path, sys, re

__doc__ = '''Convert putty public keys to openssh format

usage: %s puttykeyfile [outputfile]

 Where: outputfile defaults to 'putty.pub'

''' % Csys.Config.progname

__doc__ += '''

$Id: putty2sshpub.py,v 1.2 2009/11/25 07:52:38 csoftmgr Exp $
'''

__version__='$Revision: 1.2 $'[11:-2]

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

excmds = (
r'''$d
1d
s/.*"\(.*\)"/\1/
1m$
1
j
j
j
s/ //g
j
s/^/ssh-rsa /
wq
'''
)
print excmds

if len(args) == 1: args.append('putty.pub')
infile, outfile = args[:2]

Csys.copyfile(infile, outfile, model=infile)

excmd = Csys.popen('/usr/bin/ex - %s' % outfile, 'w')
excmd.write(excmds)
excmd.close()
sys.stderr.write('public key is in >%s<\n' % outfile)
