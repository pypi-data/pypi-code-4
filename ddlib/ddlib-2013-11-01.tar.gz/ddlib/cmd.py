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







def exe_multi(cmd_d, env=None, parent_dependent=0, exit_on_error=0):
	assert isinstance(cmd_d, dict), Exception('`cmd_d` is not <dict> !')
	finished = set()
	processes = {}
	streams = {}
	for k, v in cmd_d.items():
		if isinstance(k, str): k = k.encode()
		processes[k] = process = subprocess.Popen(
			v,
			shell = True,
			env = env,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
		)

		if parent_dependent:
			atexit.register(process.terminate)

		streams[process.stdout.fileno()] = [process.stdout, k + b'| ', [], k]
		streams[process.stderr.fileno()] = [process.stderr, k + b'|!', [], k]

	for descriptor in streams.keys():
		fcntl.fcntl(descriptor, fcntl.F_SETFL, fcntl.fcntl(descriptor, fcntl.F_GETFL) | os.O_NONBLOCK)

	while streams:
		for fd in select.select(streams.keys(), [], [])[0]:
			stream, sign, buf, name = streams.get(fd)
			buf.append(stream.read() or b'')
			if b'\n' in buf[-1]:
				tmp = b''.join(buf).split(b'\n')
				streams[fd][2] = buf = [tmp[-1]]
				for line in tmp[:-1]:
					yield b''.join((sign, line))

		streams_rm = set()
		for fd, (stream, sign, buf, name) in streams.items():
			process = processes[name]
			if process.poll() != None:
				buf.append(stream.read() or b'')
				tmp = b''.join(buf)
				if tmp:
					for line in tmp.split(b'\n'):
						yield b''.join((sign, line))

				streams_rm.add(fd)
				if name not in finished:
					finished.add(name)
					if process.returncode == 0:
						yield name + b'|!returncode-ok: 0'

					else:
						yield name + ('|!returncode-error: %s' % (process.returncode)).encode()
						if exit_on_error:
							raise Exception('CMD ERROR: %s' % cmd)

		for fd in streams_rm:
			del streams[fd]


