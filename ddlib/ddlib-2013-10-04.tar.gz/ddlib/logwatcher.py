#!/usr/bin/env python

"""
Real-time log files watcher supporting log rotation.
Works with Python >= 2.6 and >= 3.2, on both POSIX and Windows.

Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT


Modification by DDarko.org - 2013-07-02
"""

import os
import time
import errno
import stat
import sys



# TODO: dodac inotify



class LogWatcher(object):
	"""Looks for changes in all files of a directory.
	This is useful for watching log file changes in real-time.
	It also supports files rotation.

	Example:

	>>> def callback(filename, line):
	...     print(line)
	...
	>>> lw = LogWatcher("/var/log/", callback)
	>>> lw.loop()
	"""

	def __init__(self, folder, callback, extensions=["log"], exclude=None):
		"""Arguments:

		(str) @folder:
			the folder to watch

		(callable) @callback:
			a function which is called every time one of the file being
			watched is updated;
			this is called with "filename" and "lines" arguments.

		(list) @extensions:
			only watch files with these extensions

		(list) @exclude:
			do not watch this files

		"""
		self.folder = os.path.realpath(folder)
		self.extensions = extensions
		self.exclude = set(exclude) if exclude else set()
		self._files_map = {}
		self._callback = callback
		assert os.path.isdir(self.folder), self.folder
		assert callable(callback), repr(callback)

		self.update_files()
		for id, file in self._files_map.items():
			file.seek(os.path.getsize(file.name))  # EOF


	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.close()

	def __del__(self):
		self.close()


	def loop(self, interval=1.0, blocking=True):
		"""Start a busy loop checking for file changes every *interval*
		seconds. If *blocking* is False make one loop then return.
		"""
		# May be overridden in order to use pyinotify lib and block
		# until the directory being watched is updated.
		# Note that directly calling readlines() as we do is faster
		# than first checking file's last modification times.
		while True:
			self.update_files()
			for fid, file in list(self._files_map.items()):
				self.readlines(file)

			if not blocking: return
			time.sleep(interval)


	def log(self, line):
		"""Log when a file is un/watched"""
		print(line)


	def update_files(self):

		def listdir():
			"""List directory and filter files by extension.
			You may want to override this to add extra logic or globbing
			support.
			"""
			ls = set(os.listdir(self.folder))
			if self.extensions:
				ls = set(x for x in ls if os.path.splitext(x)[1][1:] in self.extensions)

			if self.exclude:
				ls -= self.exclude

			return ls

		for name in listdir():
			absname = '%s/%s' % (self.folder, name)
			try:
				st = os.stat(absname)
			except EnvironmentError as err:
				if err.errno != errno.ENOENT:
					raise
			else:
				if not stat.S_ISREG(st.st_mode):
					continue

				fid = self.get_file_id(st)
				if fid not in self._files_map:
					# add new
					self.watch(absname)

		# check existent files
		for fid, file in list(self._files_map.items()):
			try:
				st = os.stat(file.name)
			except EnvironmentError as err:
				if err.errno == errno.ENOENT:
					self.unwatch(file, fid)
				else:
					raise
			else:
				if fid != self.get_file_id(st):
					# same name but different file (rotation); reload it.
					self.unwatch(file, fid)
					self.watch(file.name)


	def readlines(self, file):
		"""Read file lines since last access until EOF is reached and
		invoke callback.
		"""
		for line in file.readlines():
			self._callback(file.name, line[:-1])


	def watch(self, fname):
		try:
			file = open(fname, 'rb')
			fid = self.get_file_id(os.stat(fname))

		except IOError as err:
			self.log(err)
			self.exclude.add(os.path.basename(fname))

		except EnvironmentError as err:
			if err.errno != errno.ENOENT:
				raise

		else:
			self.log("watching logfile %s" % fname)
			self._files_map[fid] = file


	def unwatch(self, file, fid):
		# File no longer exists. If it has been renamed try to read it
		# for the last time in case we're dealing with a rotating log
		# file.
		self.log("un-watching logfile %s" % file.name)
		del self._files_map[fid]
		with file:
			lines = self.readlines(file)
			if lines:
				self._callback(file.name, lines)


	@staticmethod
	def get_file_id(st):
		if os.name == 'posix':
			return "%xg%x" % (st.st_dev, st.st_ino)
		else:
			return "%f" % st.st_ctime


	def close(self):
		for id, file in self._files_map.items():
			file.close()
		self._files_map.clear()




