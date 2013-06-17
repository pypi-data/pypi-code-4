#!/user/local/bin/python

# $Header: /vol/cscvs/python-Csys/Xelm.py,v 1.7 2011/10/05 22:54:46 csoftmgr Exp $
# $Date: 2011/10/05 22:54:46 $

import Csys, os, os.path, sys, re

__doc__ = '''Celestial Software Main program prototype

usage: %s [options] folder [folder...]''' % Csys.Config.progname

__doc__ += '''

 Options   Argument    Description
   -c      integer     Column -- moves icon to left
   -d      directory   cd directory before spawing process.
   -m      maildir     Maildir (default ~/Maildir)
   -r                  restart (don't raise flags on mailboxes initially.
   -t      seconds     Timeout interval (default 60);
   -w                  Wide screen
   -x      position    x co-ordinate
   -y      position    y co-ordinate
   -v                  Verbose

$Id: Xelm.py,v 1.7 2011/10/05 22:54:46 csoftmgr Exp $
'''
__version__='$Revision: 1.7 $'[11:-2]

import pwd
pw = Csys.Passwd.getpwnam(pwd.getpwuid(os.getuid())[0])

USER, HOME = pw.user, pw.home

# Add program options to parser here

def setOptions(): #{
	'''Set command line options'''
	global __doc__

	parser = Csys.getopts(__doc__)

	parser.add_option('-d', '--directory',
		action='store', type='string', dest='directory', default=None,
		help='Change to directory before starting process',
	)
	parser.add_option('-m', '--maildir',
		action='store', type='string', dest='maildir',
		default= os.path.join(HOME, 'Maildir'),
		help='Mailbox file or Maildir directory',
	)
	parser.add_option('-r', '--restart',
		action='store_true', dest='restart', default=False,
		help='restart without raising mailbox flags intially',
	)
	parser.add_option('-t', '--timeout',
		action='store', type='int', dest='timeout', default=60,
		help='Time in seconds (default 60)',
	)
	return parser
#} setOptions

parser = setOptions()

(options, args) = parser.parse_args()

options.timeout *= 1000 # convert to milliseconds

if options.verbose: verbose = '-v'

Csys.getoptionsEnvironment(options)

from Csys.SysUtils import which

xterm		= which('xterm')
mutt		= which('mutt')
stty		= which('stty')
# Csys.run("%s erase '^H'" % stty)
xtermargs	= ['-geometry 80x25+0+0', '-e', mutt, '-f' ]

import Csys.Maildir, Csys.Passwd

import pkg_resources

imagedir = pkg_resources.resource_filename('Csys', 'images')
# print imagedir; sys.exit(0)

if not args: #{
	sys.stderr.write('%s\n' % __doc__)
	sys.stderr.write('No folders specified\n')
	sys.exit(1)
#}
args.sort()
from Tkinter import *

image_new = PhotoImage(file = os.path.join(imagedir, 'mail_new.gif'))
image_old = PhotoImage(file = os.path.join(imagedir, 'mail_none.gif'))
image_use = PhotoImage(file = os.path.join(imagedir, 'mail_mutt.gif'))

top = Tk()
top.iconname('xelm')
top.title('Xelm')

def mycheck(obj):
	# print 'mycheck: ', obj.folder
	obj.chk_mailsize()
#}

class Mailbox(Csys.CSClass): #{
	_attributes = {
		'maildir'			: None,
		'folder'			: None,
		'retryms'			: 60000, # milliseconds
		'frame'				: None,
		'image'				: image_old,
		'button'			: None,
		'hasnew'			: False,
		'sizechkid'			: None,
		'xtermargs'			: xtermargs[:],
		'mailsize'			: 0,
		'folderdir'			: None, # Mail box directory
		'_pid'				: 0, # pid of child xterm process
	}
	def chk_mailsize(self, newimage=None): #{
		# chk_mailsize periodically gets the size of the mailbox, and
		# compares it with the old size.  If the mailbox is larger, it
		# raises the flag, if smaller it lowers it.  It finally restarts
		# the timer to run chk_mailsize again in $opt_t milliseconds.

		# print 'chk_mailsize: %s' % self.folder
		pid = self._pid
		if pid: #{ xterm may still be running
			try: #{{
				os.kill(pid, 0)
			#}
			except OSError: #{
				pid = 0 # No such process
			#}}
			if pid: #{{
				# 10 second timeout to check for EOJ.
				self.sizechkid = self.button.after(self.retryms, mycheck, self)
			#}
			else: #{
				self._pid = 0
				self.chk_mailsize(image_old)
			#}}
			return
		#}
		if not newimage: #{{
			mailsize	= self.mailsize
			newmailsize	= self.maildir.newest(mailsize)
			if not newmailsize: #{
				newimage = image_old
			#}
			elif newmailsize > mailsize: #{
				if self.image != image_new: top.bell()
				newimage = image_new
			#}
			self.mailsize = newmailsize
		#}
		elif newimage == image_old: #{
			# reset the mail size on reset to image_old so it
			# won't immediately raise the flag.
			self.mailsize = self.maildir.newest(self.mailsize)
		#}
		if newimage: self.image = newimage
		self.button.configure(image = self.image)
		self.sizechkid = self.button.after(self.retryms, mycheck, self)
	#} chk_mailsize

	def read_email(self): #{
		'''Read email turning off timer'''
		if self._pid: #{
			top.bell()
			return
		#}
		self.image = image_use
		self.button.configure(image = image_use)
		if self.sizechkid: #{
			self.button.after_cancel(self.sizechkid)
			self.sizechkid = False
		#}
		top.update()
		pid = os.fork()
		if not pid: #{
			os.execl(xterm, *self.xtermargs)
			sys.stderr.write('exec %s failed' % xterm + ' '.join(self.xtermargs))
			sys.exit(1)
		#}
		self._pid = pid
		pidMap[pid] = self
		self.sizechkid = self.button.after(self.retryms, mycheck, self)
	#} read_email

	def checknew(self): #{
		'''Check for files in new directory'''
		if os.listdir(os.path.join(self.folderdir, 'new')): #{
			self.hasnew = True
			self.image = image_new
		#}
		else: #{
			self.hasnew = False
			self.image = image_old
		#}
	#} checknew

	def __init__(self, mailbox, folder, **kwargs): #{
		Csys.CSClass.__init__(self, **kwargs)
		self.folder = folder
		maildir	= self.maildir	= Csys.Maildir.getMaildir(mailbox, folder)
		self.folderdir			= maildir.folderdir
		self.mailsize			= maildir.newest(0)
		self.retryms			= (int(maildir.xelmretry) * 1000)
		self.xtermargs.append(self.folderdir)
		# for arg in  self.xtermargs: print arg, type(arg)
		
		f		= self.frame	= Frame(top)
		Label(f, text = folder).pack()
		self.checknew()
		button = self.button = Button(f, image = self.image, command = self.read_email)
		button.pack()
		f.pack()
		self.sizechkid = self.button.after(self.retryms, mycheck, self)
	#} __init__
#} Mailbox

import signal

pidMap = {}

def catchSIGCHLD(signo, sigframe): #{
	if(pidMap): #{
		try: pid = os.wait()[0]
		except: pid = 0
		if pid: #{
			for pid, mbox in pidMap.items(): #{
				try: #{{
					p, s = os.waitpid(pid, os.WNOHANG)
					exited = (os.WIFEXITED(s) or os.WIFSIGNALED(s))
				#}
				except OSError: #{
					exited = True
				#}}
				if exited: #{
					try: #{{
						os.kill(pid, 0)
						pid = 0
					#}
					except OSError: #{
						pass
					#}}
					if pid: #{
						del pidMap[pid]
						mbox._pid = 0
						mbox.chk_mailsize(image_old)
					#}
				#}
			#}
		#}
	#}
	signal.signal(signal.SIGCHLD, catchSIGCHLD)
#} def catchSIGCHLD

signal.signal(signal.SIGCHLD, catchSIGCHLD)

for folder in args: #{
	f = Mailbox(options.maildir, folder)
#}

top.mainloop()
