# Subprocess containers
"""
	A mechanism to run subprocesses asynchronously and with non-blocking read.
"""
import atexit
import multiprocessing
import Queue
import subprocess
import sys
import threading
import time

class Group:
	"""
		Runs a subprocess in parallel, capturing it's output and providing non-blocking reads (well, at
		least for the caller they appear non-blocking).
	"""
	def __init__(self):
		self.output = Queue.Queue()
		self.handles = []
		self.waiting = 0
		
	def run( self, cmd, shell = False ):
		"""
			Adds a new process to this object. This process is run and the output collected.
			
			@param cmd: the command to execute, as in subprocess.Popen
			@return the handle to the process return from Popen
		"""
		handle = subprocess.Popen( cmd,
			shell = shell,
			bufsize = 1,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT,
			stdin = subprocess.PIPE, # needed to detach from calling terminal (other wacky things can happen)
		)
		handle.group_output_done = False
		self.handles.append( handle )
		
		# a thread is created to do blocking-read
		self.waiting += 1
		def block_read():
			try:
				for line in iter( handle.stdout.readline, '' ):
					self.output.put( ( handle, line ) )
			except:
				pass
				
			# To force return of any waiting read (and indicate this process is done
			self.output.put( ( handle, None ) )
			handle.stdout.close()
			self.waiting -= 1
			
		block_thread = threading.Thread( target = block_read )
		block_thread.daemon = True
		block_thread.start()
			
		# kill child when parent dies
		def premature_exit():
			try: 
				handle.terminate()
			except:
				pass # who cares why, we're exiting anyway (most likely since it is already terminated)
		atexit.register( premature_exit )
			
		return handle
		
	def readlines( self, max_lines = 1000,  timeout = 2.0 ):
		"""
			Reads available lines from any of the running processes. If no lines are available now
			it will wait until 'timeout' to read a line. If nothing is running the timeout is not waited
			and the function simply returns.
			
			When a process has been completed and all output has been read from it, a
			variable 'group_ouput_done' will be set to True on the process handle.
			
			@param timeout: how long to wait if there is nothing available now
			@param max_lines: maximum number of lines to get at once
			@return: An array of tuples of the form:
				( handle, line )
				There 'handle' was returned by 'run' and 'line' is the line which is read.
				If no line is available an empty list is returned.
		"""
		lines = []
		try:
			while len(lines) < max_lines:
				handle, line = self.output.get_nowait()
				# interrupt waiting if nothing more is expected
				if line == None:
					handle.group_output_done = True
					if self.waiting == 0:
						break
				else:
					lines.append( ( handle, line ) )
			return lines
			
		except Queue.Empty:
			# if nothing yet, then wait for something
			if len(lines) > 0 or self.waiting == 0:
				return lines
			
			item = self.readline( timeout = timeout )
			if item != None:
				lines.append( item )
			return lines
			
	def readline( self, timeout = 2.0 ):
		"""
			Read a single line from any running process.
			
			Note that this will end up blocking for timeout once all processes have completed.
			'readlines' however can properly handle that situation and stop reading once
			everything is complete.
			
			@return: Tuple of ( handle, line ) or None if no output generated.
		"""
		try:
			handle, line = self.output.get( timeout = timeout )
			if line == None:
				handle.group_output_done = True
				return None
			return (handle, line)
		except Queue.Empty:
			return None

	def is_pending( self ):
		"""
			Determine if calling readlines would actually yield any output. This returns true
			if there is a process running or there is data in the queue.
		"""
		if self.waiting > 0:
			return True
		return not self.output.empty()
		
	def count_running( self ):
		"""
			Return the number of processes still running. Note that although a process may
			be finished there could still be output from it in the queue. You should use 'is_pending'
			to determine if you should still be reading.
		"""
		count = 0
		for handle in self.handles:
			if handle.poll() == None:
				count += 1
		return count
		
	def get_exit_codes( self ):
		"""
			Return a list of all processes and their exit code.
			
			@return: A list of tuples:
				( handle, exit_code )
				'handle' as returned from 'run'
				'exit_code' of the process or None if it has not yet finished
		"""
		codes = []
		for handle in self.handles:
			codes.append( ( handle, handle.poll() ) )
		return codes
		
	def clear_finished( self ):
		"""
			Remove all finished processes from the managed list.
		"""
		nhandles = []
		for handle in self.handles:
			if not handle.group_output_done or handle.poll() == None:
				nhandles.append( handle )
		self.handles = nhandles
