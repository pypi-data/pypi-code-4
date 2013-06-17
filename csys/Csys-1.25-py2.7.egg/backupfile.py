#!/usr/local/bin/python

# $Header: /vol/cscvs/python-Csys/backupfile.py,v 1.1 2009/11/25 01:44:52 csoftmgr Exp $
# $Date: 2009/11/25 01:44:52 $

import Csys, os, os.path, sys, re

__doc__ = '''Back up file to backups directory maintaining copies

usage: %s filename [filename ...]''' % Csys.Config.progname

__doc__ += '''

$Id: backupfile.py,v 1.1 2009/11/25 01:44:52 csoftmgr Exp $
'''

__version__='$Revision: 1.1 $'[11:-2]

class BackupFile(object): #{
	'''
	The primary purpose of this class is to provide a simple
	method of sorting the files on the numeric suffix.  It also
	has a routine that moves older files up the chain of files
	that have been backed up (e.g. filename.0 ->filename.1...)
	'''
	def __init__(self, fname): #{
		basename, ext = os.path.splitext(fname)
		self.fname = fname
		self.prefix = os.path.join(os.path.dirname(fname), basename)
		self.suffix = int(ext[1:])
	#}
	def __cmp__(self, othr): #{
		return(cmp((self.prefix, -self.suffix), (othr.prefix, -othr.suffix)))
	#}
	def moveUp(self): #{
		new = '%s.%02d' % (self.prefix, self.suffix + 1)
		os.rename(self.fname, new)
		# print 'mv %s %s' % (self.fname, new)
	#}
#} class BackupFile

def main(): #{
	# Add program options to parser here

	def setOptions(): #{
		'''Set command line options'''
		global __doc__

		parser = Csys.getopts(__doc__)

		parser.add_option('-c', '--copies',
			action='store', type='int', dest='copies', default=9,
			help='Number of copies to keep',
		)
		parser.add_option('-b', '--backupdir',
			action='store', type='string', dest='backupdir',
			default='',
			help='Backup directory (default same as file)',
		)
	#	parser.add_option('-r', '--restart',
	#		action='store_true', dest='restart', default=False,
	#		help='restart without raising mailbox flags intially',
	#	)
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
	from glob import glob
	backupDir = options.backupdir
	for arg in args: #{
		dname, fname = os.path.split(arg)
		backups = backupDir or dname or '.'
		needBackup = not os.path.exists(backups)
		if needBackup: #{
			Csys.mkpath(backups)
		#}
		firstBackup = os.path.join(backups, fname) + '.0'
		if not needBackup: #{
			needBackup = not os.path.exists(firstBackup)
			if not needBackup: #{
				fileInfoOld = Csys.FileInfo(firstBackup, True)
				fileInfoNew = Csys.FileInfo(arg, True)
				needBackup = fileInfoOld.md5 != fileInfoNew.md5
			#}
		#}
		if needBackup: #{
			backupFiles = sorted([
				BackupFile(file) for file in glob('%s/%s.*' % (backups, fname))
			])
			for backupFile in backupFiles: #{
				if backupFile.suffix < options.copies: #{
					backupFile.moveUp()
				#}
			#}
			Csys.run('gcp -p %s %s' % (arg, firstBackup), verbose)
		#}
	#}
#}
if __name__ == '__main__': #{
	main()
#}
