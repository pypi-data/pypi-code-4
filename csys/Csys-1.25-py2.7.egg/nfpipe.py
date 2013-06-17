#!/csrel27a/bin/python

# $Header: /vol/cscvs/python-Csys/csmain.py,v 1.4 2009/11/25 07:49:41 csoftmgr Exp $
# $Date: 2009/11/25 07:49:41 $

# This processes the output with a loginfo entry:
# DEFAULT	/csrel22/bin/nfpipe -r %r -p %p -s "%s"

import Csys, os, os.path, sys, re
import time
timefmt = '%a %b %d %H:%M:%S %Z %Y'
runtime = time.strftime(timefmt, time.localtime())

__doc__ = '''Celestial Software Main program prototype

usage: %s''' % Csys.Config.progname

__doc__ += '''

$Id: csmain.py,v 1.4 2009/11/25 07:49:41 csoftmgr Exp $
'''

__version__='$Revision: 1.4 $'[11:-2]

def main(): #{
	# Add program options to parser here

	def setOptions(): #{
		'''Set command line options'''
		global __doc__

		parser = Csys.getopts(__doc__)

		parser.add_option('-d', '--debugfile',
			action='store', type='string', dest='debugfile',
			default=os.path.join(
				os.path.expanduser('~/tmp/cvs'),
				os.path.splitext(Csys.Config.progname)[0] + '.log'
			),
			help='Debug Output in this file',
		)
		parser.add_option('--sleeptime',
			action='store', type='int', dest='sleeptime',
			default=5, help='Sleep Time in Seconds (default 5)'
		)
		parser.add_option('-r', action='store', type='string', help='%r', default='')
		parser.add_option('-p', action='store', type='string', help='%p', default='')
		parser.add_option('-s', action='store', type='string', help='%s', default='')
		
	#	parser.add_option('-r', '--restart',
	#		action='store_true', dest='restart', default=False,
	#		help='restart without raising mailbox flags intially',
	#	)
		return parser
	#} setOptions

	parser = setOptions()

	(options, args) = parser.parse_args()
	opt = options

	verbose = ''
	if options.sleeptime <= 0: #{
		sys.stderr.write("Sleep time %d less than 0" % options.sleeptime)
	#}
	print options.sleeptime
	if True or options.verbose: #{
		verbose = '-v'
		sys.stdout = sys.stderr
	#}
	Csys.getoptionsEnvironment(options)
	debugfile = options.debugfile
	debugdir = debugfile and os.path.dirname(debugfile) or ''
	if not os.path.isdir(debugdir): Csys.mkpath(debugdir, mode=0700)
	debugfile = Csys.Logger('nfpipe', logfile = debugfile)
	# sys.stdout = sys.stderr = debugfile
	# debugfile.write( 'start' )
	output = ['start']
	if False: #{
		maxl = 0
		keys = sorted(os.environ.keys())
		for key in keys: #{
			maxl = max(len(key), maxl)
		#}
		fmt = '%%-%ds %%s' % maxl
		for key in keys: #{
			output.append(fmt % (key, os.environ[key]))
		#}
		output.append('')
	#}
	lines = ['\t' + s.rstrip() for s in sys.stdin.readlines()]
	# print repr(lines)
	if verbose: #{
		debugfile.write('\n'.join(output))
		cols = options.__dict__
		for opt in ('r', 'p', 's'): #{
			output.append('opt_%s = >%s<' % (opt, cols[opt]))
		#}
		debugfile.write('\n'.join(output))
	#}
	if options.s != 'Changes': #{
		Root = (options.r or open('CVS/Root').readline().rstrip())
		Repository = (options.p or open('CVS/Repository').readline().rstrip())
		checkout = ('cvs -d "%s" co "%s/Changes" > debug 2>&1' % (Root, Repository))
		if verbose: output.append('Repository (%s)' % Repository)
		output.append('checkout (%s)' % checkout)
		rcs_Changes = os.path.join(options.r, Repository, 'Changes,v')
		if verbose: #{
			output.append('rcs_Changes (%s)' % rcs_Changes)
		#}
		dname = '%s.%d' % (debugdir, int(time.time()))
		tmpdir = os.path.join(
			debugdir,
			'work.%d' % int(time.time())
		)
		Csys.mkpath(tmpdir)
		os.chdir(tmpdir)
		pid = os.fork()
		if pid: #{
			# I'm the parent and I need to go away for the calling process
			# to finish its work.
			sys.exit(0)
		#}
		sys.stdout = sys.stderr = debugfile
		time.sleep(options.sleeptime) # the parent needs time to finish
		Csys.run(checkout)
		os.chdir(Repository)
		changes = 'Changes'
		if os.path.isfile(changes): #{
			changes = open(changes, 'a')
			chgout = [
				runtime,
				'\tUpdate by %s' % os.environ['USER']
			]
			SSH_CLIENT = os.environ.get('SSH_CLIENT', '').split()[0]
			if SSH_CLIENT: #{
				chgout.append('\tRemote from ' + SSH_CLIENT)
			#}
			chgout.extend(lines)
			chgout.append('')
			changes.write('\n'.join(chgout))
			changes.close()
			cmd = 'cvs ci -m "" Changes < /dev/null > debug 2>&1'
			debugfile.write(cmd)
			Csys.run(cmd)
		#}
		debugfile.write('stop')
	#}
#}
if __name__ == '__main__': #{
	main()
#}
