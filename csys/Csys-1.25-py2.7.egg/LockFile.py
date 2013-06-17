#!/csoft/bin/python

__doc__='''File Locking Utilities, similar to perl LockFile::Simple

use Csys.LockFile

# Create a lock object locking file if doLock is True
lock = Csys.LockFile.Simple(filename, doLock, [options])
lock.unlock() # unlock the file
lock.lock() # (re)lock the file

Locked files contain the process ID of the locking process, and
will be removed if that process isn't currently running.

By default, the lockfile name is the same as the file to be locked
with a .lock suffix.

Any lockfiles will automatically be removed upon program exit.

$Id: LockFile.py,v 1.3 2011/10/05 19:43:55 csoftmgr Exp $'''

__version__='$Revision: 1.3 $'[11:-2]

import os, sys, re, time, stat, socket
from os.path import basename, dirname

class Error(Exception): #{
    '''Base class for Csys.Passwd exceptions'''
    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__
#} class Error

_myhostname = socket.gethostname()

def no_warn(msg): pass

_lockedFiles = {}

class Simple: #{
	'''Similar to perl LockFile::Simple object'''
	_attributes = {
		'max'			: 30,
		'delay'			: 2,
		'hold'			: 3600,
		'ext'			: '.lock',
		'nfs'			: False,
		'stale'			: True,
		'warn'			: False,
		'wmin'			: 15,
		'wafter'		: 20,
		'autoclean'		: False,
		'lock_by_file'	: {},
		'wfunc'			: sys.stderr.write,
		'efunc'			: None,
		'format'		: None,
	} # _attributes
	def __init__(self, file, dolock, **kwargs): #{
		'''Initialize lock. if dolock is true, get lock'''
		global _lockedFiles
		_lockedFiles[file] = self
		self.file = file
		d = self.__dict__
		d.update(self._attributes)
		for key, val in kwargs.items(): #{
			if key in d: d[key] = val
			else: raise Error('Simple: invalid key %s' % key)
		#}
		if not self.wfunc: self.warn = False
		self._acs_genLockfile() # sets self.stamp and self.lockfile
		self.is_locked = False
		if dolock: self.lock()
	#} __init__

	def trylock(self): #{
		return self.lock(True)
	#} trylock

	def unlock(self): #{
		'''Unlock file'''
		lockfile = self.lockfile
		if self.is_locked: #{
			if os.access(lockfile, os.F_OK): #{
				fh = open(lockfile, 'r')
				l = fh.readline().rstrip()
				fh.close()
				if l == self.stamp: #{
					try: os.unlink(lockfile)
					except:
						raise Error('unlock: cannot unlink lockfile %s' % lockfile)
					else: self.is_locked = False
				#}
				else: raise Error('unlock: cannot lock %s owned by %s' % ( lockfile, l))
			#}
			else: self.is_locked = False
		#}
		return self.is_locked
	#} unlock

	def __del__(self): #{
		'''Unlock file when object deleted (automatic cleanup)'''
		self.unlock()
		global _lockedFiles
		try: _lockedFiles.pop(self.file)
		except: pass
	#} __del__

	def _lockfile(self): #{
		'''Return name of the lockfile'''
		file, format = self.file, self.format
		format = re.sub(r'%%', r'\01', format) # protect %%
		format = re.sub(r'%', r'\02', format)
		format = re.sub(r'\02f', file, format)
		format = re.sub(r'\02D', lambda x, s=file: dirname(s), format)
		format = re.sub(r'\02F', lambda x, s=file: basename(s), format)
		format = re.sub(r'\02', '%')
		format = re.sub(r'\01', '%')
		return format
	#} _lockfile

	def _acs_genLockfile(self): #{
		'''Return tuple (stamp, format, lockfile)'''
		file, format, ext = (self.file, self.format, self.ext)
		stamp = '%d' % os.getpid()
		if self.nfs: #{
			ext = '.%d:%s.lock' % (stamp, _myhostname)
			stamp += ':' + _myhostname
		#}
		if format: lockfile = self._lockfile()
		else: lockfile = file + ext

		self.stamp = stamp
		self.lockfile = lockfile
		return(stamp, lockfile)
	#} _acs_genLockfile 

	def lock(self, tryonly=False): #{
		'''Internal locking routine'''
		if self.is_locked: return True
		file, format, max, delay = (self.file, self.format, self.max, self.delay)

		# detect stale locks or break lock if held for too long
		if self.stale: self._acs_stale()
		if self.hold: self._acs_check()
		waited = lastwarn = 0
		warn = self.warn
		wmin, wafter, wfunc = (None, None, None)
		if self.warn: wmin, wafter, wfunc = self.wmin, self.wafter, self.wfunc
		locked = False
		mask = os.umask(0333)
		whileCount = 0
		while max > 0: #{
			max -= 1
			if whileCount: #{
				'''This is a funny implementation of a perl while continue'''
				time.sleep(delay)
				waited += delay
				# Warn them once after $wmin seconds and then every $wafter seconds
				if ( warn and ( (not lastwarn and waited > wmin) or (waited - lastwarn) > wafter)): #{
					waiting = 'waiting'
					after = 'since'
					if lastwarn: #{
						waiting = 'still waiting'
						after = 'after'
					#}
					s = ''
					if waited > 1: s = 's'
					wfunc('%s for %s lock %s %s %s\n' % (
						waiting, file, after, waited, s
					))
				#}
				# While we wait, existing lockfile may become stale or too old
				if self.stale: self._acs_stale()
				if self.hold: self._acs_check()
			#}
			whileCount += 1
			lockfile = self.lockfile
			if os.access(lockfile, os.F_OK): #{
				'''File Exists'''
				if self.warn: self.wfunc('lockfile >%s< exists\n' % lockfile)
				if not tryonly: continue
				os.umask(mask)
				self.is_locked = False
				return False
			#}
			# attempt to create lock
			try: fh = open(lockfile, 'w')
			except IOError, err:
				if str(err).find('Permission denied') != -1: #{{
					'''File Exists'''
					if self.warn: self.wfunc('lockfile >%s< exists\n' % lockfile)
					if not tryonly: continue
					os.umask(mask)
					self.is_locked = False
					return False
				#}
				else: #{
					raise Error('lock: %s' % err)
				#}}
			except: #{
				if self.warn: self.wfunc('open(%s) failed\n' % lockfile)
				if tryonly: #{
					os.umask(mask)
					self.is_locked = False
					return False
				#}
				continue
			#}
			stamp = self.stamp
			fh.write('%s\n' % stamp)
			fh.close()
			fh = open(lockfile)
			l = fh.readline().rstrip()
			locked = (l == stamp)
			if locked: #{
				try: l = fh.next()
				except: pass
				else: locked = False
			#}
			fh.close()
			if locked: break
		#}
		self.is_locked = locked
		os.umask(mask)
		return locked
	#} _acs_lock

	def _acs_check(self): #{
		'''Check for old lock files, removing if old'''
		lockfile = self.lockfile
		try: mtime = os.stat(lockfile)[stat.ST_MTIME]
		except: return # presumably there's no file
		hold = self.hold
		# if file too old to be considered stale?
		if int(time.time()) - mtime > hold: #{
			# RACE CONDITION
			try: os.unlink(lockfile)
			except: raise Error('Cannot unlink %s' % lockfile)
			if self.warn: #{
				msg = 'UNLOCKED %s (lock older than %d second\n' % ( file, hold )
				if hold > 1: msg += 's'
				self.wfunc(msg)
			#}
		#}
	#} _acu_check

	def _acs_stale(self): #{
		'''Remove stale locks using os.kill() to see if process is alive'''
		lockfile = self.lockfile
		try: #{{
			fh = open(lockfile)
			stamp = fh.readline().rstrip()
			fh.close()
		#}
		except: #{
			return # presumably the open failed
		#}}
		if self.nfs: #{{
			n = stamp.find(':')
			if n == -1: return
			pid, hostname = stamp.split(':')
			if _myhostname != hostname: return
			hostname = 'on ' + hostname
		#}
		else: #{
			hostname = ''
			pid = stamp
		#}}
		if pid: #{
			try: #{{
				pid = int(pid)
				os.kill(pid, 0)
			#}
			except: #{
				pass
			#}
			else: #{
				return
			#}}
		#}
		else: pid = -1
		# RACE CONDITION -- shall we lock the lockfile?
		try: os.unlink(lockfile)
		except: raise Error('cannot unlink stale %s' % lockfile)
		
		if self.warn: #{
			self.wfunc('UNLOCKED %s (stale lock by PID %d%s\n' % (
				lockfile, pid, hostname))
		#}
	#} _acs_stale

#} class Simple

def lockFile(file, doLock=True, **kwargs): #{
	'''Create a Simple lock file object or return existing one'''
	if file in _lockedFiles: #{
		return(_lockedFiles[file])
	#}
	return Simple(file, doLock, **kwargs)
#} lockFile

if __name__ == '__main__': #{
	print 'OK'
#}
