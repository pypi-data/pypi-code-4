#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/undelsend.py,v 1.2 2009/11/25 07:59:48 csoftmgr Exp $
# $Date: 2009/11/25 07:59:48 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: undelsend.py,v 1.2 2009/11/25 07:59:48 csoftmgr Exp $
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

from Csys.MailInternet import MBOX

try:				undelmail = args[0]
except IndexError:	undelmail = '/root/Undel.mail'

try: size = os.path.getsize(undelmail)
except: size = 0
if not size: #{
	sys.stderr.write('%s is empty or nonexistent\n' % undelmail)
	sys.exit(0)
#}
undelsave = undelmail + '.save'
os.rename(undelmail, undelsave)

mbox = MBOX(undelsave)

sendmail = Csys.Config.sendmail

while True: #{
	msg = mbox.nextMessage()
	if not msg: break
	to = msg.get('X-Original-To')
	msg.delete('X-Original-To')
	msg.delete('X-Delivered')
	msg.delete('Delivered-To')
	msg.delete('Status')
	cmd = '%s %s' % (sendmail, to)
	sys.stderr.write('%s\n' % cmd)
	fh = Csys.popen(cmd, 'w')
	fh.write(str(msg))
	fh.close()
#}
