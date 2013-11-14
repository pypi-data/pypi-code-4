#!/usr/bin/env python3

import os
import sys
import time
import fcntl
import atexit
import select
import subprocess




def exe(cmd, env=None, shell=False, parent_dependent=0, exit_on_error=1):
	try:
		process = subprocess.Popen(
			cmd,
			shell = shell,
			env = env,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
		)

	except Exception as e:
		es = str(e)
		returncode = es.split(']', 1)[0].rsplit(' ', 1)[-1] if ']' in es else 2
		yield ('!%s : %s' % (cmd, e)).encode()
		yield ('!returncode-error: %s' % returncode).encode()
		if exit_on_error:
			raise Exception('CMD ERROR: {0}'.format(cmd))

	else:
		if parent_dependent:
			atexit.register(process.terminate)

		streams = {
			process.stdout.fileno(): [process.stdout, b' ', []],
			process.stderr.fileno(): [process.stderr, b'!', []],
		}

		#for descriptor in streams.keys():
		#	fcntl.fcntl(descriptor, fcntl.F_SETFL, fcntl.fcntl(descriptor, fcntl.F_GETFL) | os.O_NONBLOCK)

		while 1:
			for fd in select.select(streams.keys(), [], [])[0]:
				stream, sign, buf = streams.get(fd)
				s = stream.read()
				if s:
					buf.append(s)
					if b'\n' in buf[-1]:
						tmp = b''.join(buf).split(b'\n')
						streams[fd][2] = buf = [tmp[-1]]
						for line in tmp[:-1]:
							yield sign + line

			if process.poll() != None:
				for stream, sign, buf in streams.values():
					s = stream.read()
					if s:
						buf.append(s)
						tmp = b''.join(buf)
						if tmp:
							for line in tmp.split(b'\n'):
								yield sign + line

				if process.returncode == 0:
					yield b'!returncode-ok: 0'

				else:
					yield ('!returncode-error: %s' % process.returncode).encode()
					if exit_on_error:
						raise Exception('CMD ERROR: {0}'.format(cmd))

				break





def sh(cmd, remove_sign_prefix=True):
	tmp = list(exe(cmd, shell=True, exit_on_error=0))
	if remove_sign_prefix: tmp = [x[1:] for x in tmp]
	return int(tmp[-1].split(b': ')[1]), tmp[:-1]




class Executor:
	"""
		e = cmd.Executor()
		e.run('tail', 'tailf /proc/filesystems')
		e.run('ls', 'ls /tmp33')
		e.run('sleep', 'sleep 5')

		for l in e.readline():
			print('cmd count:', len(e))
			if l is not None:
				print(l)
				if b'!returncode-error:' in l:
					e.run('echo', 'echo "cmd error!"')
	"""

	def __init__(self):
		self.interval = 2
		self.__processes = {}
		self.__descriptors = {}
		self.__buffor = []



	def __len__(self):
		"""
			ile mamy uruchomionych polecen
		"""
		return len(self.__processes)



	def run(self, name, cmd, env=None, shell=False):
		"""
			uruchamiamy nowe polecenie
		"""
		if isinstance(name, str): name = name.encode()
		if name in self.__processes: raise Exception('name `%s` is already taken !' % name.decode())

		try:
			self.__processes[name] = process = subprocess.Popen(
				cmd,
				shell = shell,
				env = env,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE
			)

		except Exception as e:
			es = str(e)
			returncode = es.split(']', 1)[0].rsplit(' ', 1)[-1] if ']' in es else 2
			self.__buffor.append( name + ('|!%s : %s' % (cmd, e)).encode() )
			self.__buffor.append( name + ('|!returncode-error: %s' % returncode).encode() )

		else:
			atexit.register(process.terminate)

			fd1 = process.stdout.fileno()
			fd2 = process.stderr.fileno()
			self.__descriptors[fd1] = [process.stdout, name + b'| ', [], name]
			self.__descriptors[fd2] = [process.stderr, name + b'|!', [], name]

			#fcntl.fcntl(fd1, fcntl.F_SETFL, fcntl.fcntl(fd1, fcntl.F_GETFL) | os.O_NONBLOCK)
			#fcntl.fcntl(fd2, fcntl.F_SETFL, fcntl.fcntl(fd2, fcntl.F_GETFL) | os.O_NONBLOCK)



	def readline(self):
		"""
			iterujemy po liniach wyjscia
		"""
		while 1:
			if self.__buffor:
				for x in xrange(len(self.__buffor)):
					yield self.__buffor.pop(0)

			if self.__descriptors:
				for fd in select.select(self.__descriptors.keys(), [], [], self.interval)[0]:
					stream, sign, buf, name = self.__descriptors[fd]
					s = stream.read()
					if s:
						buf.append(s)
						if b'\n' in buf[-1]:
							tmp = b''.join(buf).split(b'\n')
							self.__descriptors[fd][2] = buf = [tmp[-1]]
							for line in tmp[:-1]:
								yield sign + line

				else:
					# zaden z procesow nic nie zwraca przez 2s
					yield

				for name in sorted(self.__processes):
					process = self.__processes.get(name)
					if process and process.poll() != None:
						for fd in [k for k, v in self.__descriptors.items() if v[3] == name]:
							stream, sign, buf, name = self.__descriptors[fd]
							s = stream.read()
							if s:
								buf.append(s)
								tmp = b''.join(buf)
								if tmp:
									for line in tmp.split(b'\n'):
										yield sign + line

							del self.__descriptors[fd]

						del self.__processes[name]
						try: atexit.unregister(process.terminate)
						except Exception: pass

						if process.returncode == 0:
							yield name + b'|!returncode-ok: 0'

						else:
							yield name + ('|!returncode-error: %s' % (process.returncode)).encode()

			else:
				# brak procesow do obserwowania
				time.sleep(self.interval)
				yield
