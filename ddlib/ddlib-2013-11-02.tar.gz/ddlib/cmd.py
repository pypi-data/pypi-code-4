#!/usr/bin/env python3

import os
import sys
import time
import fcntl
import atexit
import select
import subprocess




def exe(cmd, env=None, parent_dependent=0, exit_on_error=1, host=None):
	if host:
		cmd = 'ssh %s "%s"' % (host, cmd)

	process = subprocess.Popen(
		cmd,
		shell = True,
		env = env,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE
	)

	if parent_dependent:
		atexit.register(process.terminate)

	streams = {
		process.stdout.fileno(): [process.stdout, b' ', []],
		process.stderr.fileno(): [process.stderr, b'!', []],
	}

	for descriptor in streams.keys():
		fcntl.fcntl(descriptor, fcntl.F_SETFL, fcntl.fcntl(descriptor, fcntl.F_GETFL) | os.O_NONBLOCK)

	while True:
		for fd in select.select(streams.keys(), [], [])[0]:
			stream, sign, buf = streams.get(fd)
			buf.append(stream.read() or b'')
			if b'\n' in buf[-1]:
				tmp = b''.join(buf).split(b'\n')
				streams[fd][2] = buf = [tmp[-1]]
				for line in tmp[:-1]:
					yield b''.join((sign, line))

		if process.poll() != None:
			for stream, sign, buf in streams.values():
				buf.append(stream.read() or b'')
				tmp = b''.join(buf)
				if tmp:
					for line in tmp.split(b'\n'):
						yield b''.join((sign, line))

			if process.returncode == 0:
				yield b'!returncode-ok: 0'

			else:
				yield ('!returncode-error: %s' % process.returncode).encode()
				if exit_on_error:
					raise Exception('CMD ERROR: %s' % cmd)

			break










class Executor:
	"""
		e = cmd.Executor()
		e.run('tail', 'tailf /proc/filesystems')
		e.run('ls', 'ls /tmp33')
		e.run('sleep', 'sleep 5')

		while len(e):
			print('cmd count: %s' % len(e))
			for l in e.readline():
				print(l)
				if b'!returncode-error:' in l:
					e.run('echo', 'echo "cmd error!"')
	"""

	def __init__(self):
		self.__processes = {}
		self.__descriptors = {}



	def __len__(self):
		"""
			ile mamy uruchomionych polecen
		"""
		return len(self.__processes)



	def run(self, name, cmd, env=None):
		"""
			uruchamiamy nowe polecenie
		"""
		if isinstance(name, str): name = name.encode()
		if name in self.__processes: raise Exception('name `%s` is already taken !' % name.decode())
		self.__processes[name] = process = subprocess.Popen(
			cmd,
			shell = True,
			env = env,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
		)

		atexit.register(process.terminate)

		fd1 = process.stdout.fileno()
		fd2 = process.stderr.fileno()
		self.__descriptors[fd1] = [process.stdout, name + b'| ', [], name]
		self.__descriptors[fd2] = [process.stderr, name + b'|!', [], name]

		fcntl.fcntl(fd1, fcntl.F_SETFL, fcntl.fcntl(fd1, fcntl.F_GETFL) | os.O_NONBLOCK)
		fcntl.fcntl(fd2, fcntl.F_SETFL, fcntl.fcntl(fd2, fcntl.F_GETFL) | os.O_NONBLOCK)



	def readline(self):
		"""
			iterujemy po liniach wyjscia
		"""
		if self.__descriptors:
			for fd in select.select(self.__descriptors.keys(), [], [])[0]:
				stream, sign, buf, name = self.__descriptors[fd]
				buf.append(stream.read() or b'')
				if b'\n' in buf[-1]:
					tmp = b''.join(buf).split(b'\n')
					self.__descriptors[fd][2] = buf = [tmp[-1]]
					for line in tmp[:-1]:
						yield b''.join((sign, line))

			for name in sorted(self.__processes):
				process = self.__processes.get(name)
				if process and process.poll() != None:
					for fd in [k for k, v in self.__descriptors.items() if v[3] == name]:
						stream, sign, buf, name = self.__descriptors[fd]
						buf.append(stream.read() or b'')
						tmp = b''.join(buf)
						if tmp:
							for line in tmp.split(b'\n'):
								yield b''.join((sign, line))

						del self.__descriptors[fd]

					if process.returncode == 0:
						yield name + b'|!returncode-ok: 0'

					else:
						yield name + ('|!returncode-error: %s' % (process.returncode)).encode()

					del self.__processes[name]
					try: atexit.unregister(process.terminate)
					except Exception: pass

		else:
			# brak procesow do obserwowania
			time.sleep(1)
