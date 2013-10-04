import os
import sys
import fcntl
import select
import datetime
import subprocess

from . import log_debug, log_info, log_error


def bash(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = p.communicate()
	return p.returncode, stdout.decode(), stderr.decode()



def run(host, cmd, suppres_log=0, exit_on_error=1):
	if host != 'local': cmd = 'ssh %s "%s"' % (host, cmd)
	r, stdout, stderr = bash(cmd)
	stdout = stdout.strip()
	stderr = stderr.strip()
	if not suppres_log:
		if r != 0 or stderr:
			log_info('-'*60)
			log_info('HOST: %s CMD: %s' % (host, cmd))
			if r != 0: log_error('!!! return code: %s' % r)
			if stderr:
				log_error('--- stderr:')
				log_error(stderr)

			if stdout:
				log_info('--- stdout:')
				log_info(stdout)

			log_info('-'*60)

	if exit_on_error and r != 0:
		exit(1)

	return stdout






def exe(cmd, exit_on_error=1, host=None, env=None):
	if host:
		cmd = 'ssh %s "%s"' % (host, cmd)

	p = subprocess.Popen(
		cmd,
		shell = True,
		env = env,
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE
	)

	# descriptor: (stream, buffor, sign)
	streams = {
		p.stdout.fileno(): (p.stdout, b'', ' '),
		p.stderr.fileno(): (p.stderr, b'', '!'),
	}

	for descriptor in streams.keys():
		fcntl.fcntl(descriptor, fcntl.F_SETFL, fcntl.fcntl(descriptor, fcntl.F_GETFL) | os.O_NONBLOCK)

	while True:
		for fd in select.select(streams.keys(), [], [])[0]:
			stream, buf, sign = streams.get(fd)
			buf += stream.read() or b''
			if b'\n' in buf:
				tmp = buf.split(b'\n')
				buf = tmp[-1]
				for line in tmp[:-1]:
					yield ''.join((sign, line.decode()))

		if p.poll() != None:
			for stream, buf, sign in streams.values():
				buf += stream.read() or b''
				if buf:
					for line in buf.split(b'\n'):
						yield ''.join((sign, line.decode()))

			break

	if p.returncode != 0:
		yield '!returncode: %s\n' % p.returncode
		if exit_on_error:
			raise Exception('RUN CMD: %s' % cmd)



