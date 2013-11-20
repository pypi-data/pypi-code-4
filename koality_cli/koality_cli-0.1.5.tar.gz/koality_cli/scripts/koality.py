#!/usr/bin/env python
# The following must use spaces instead of tabs for alignment purposes
"""Koality client that simplfies workflows.
Wraps the git and hg client.

Usage:
  ko help
  ko generate [--debug]
  ko commit [ARGS...]
  ko push [ARGS...]
  ko <command> [ARGS...]

Options:
  -h --help    Show this message
  --version    Show version

Details:
  help                - print this message
  generate            - attempt to autocreate a config koality.yml in the 
                        repo root that will work in most cases but in some
                        instances may need modifications to properly work
  push                - perform a push that is automatically pre verified
                        by Koality before merging into the repo
  <command>           - shell out to git to run a command
"""

full_doc = """Koality client that simplfies workflows.
Wraps the git and hg client.

Usage:
  ko help
  ko login
  ko upload-keys
  ko generate
  ko commit [ARGS...]
  ko push [ARGS...]
  ko push-unchecked [ARGS...]
  ko test [ARGS...]
  ko update
  ko <command> [ARGS...]

Options:
  -h --help    Show this message
  --version    Show version

Details:
  help                - print this message
  login               - login to your Koality instance to perform commands
  upload-keys         - auto upload ssh keys to your Koality instance
  generate            - attempt to autocreate a config koality.yml in the 
                        repo root that will work in most cases but in some
                        instances may need modifications to properly work
  push                - perform a push that is automatically pre verified
                        by Koality before merging into the repo
  push-unchecked      - perform a push that skips Koality verification and
                        immediately goes into the repo
  test                - use Koality to only test your changes without merging
  update              - update the Koality cli
  <command>           - shell out to git to run a command
"""

import os.path
import sys
import subprocess

import koality_cli

from docopt import docopt

from koality_cli.config_creator import ConfigCreator


class CliHandler(object):
	REPO_NOT_FOUND_ERROR_CODE = 1
	UNKNOWN_ERROR_CODE = 255

	def handle(self, options, arguments):
		def run_vanilla_vcs_command(command):
			try:
				vcs = self._repo_type()
				return subprocess.call([vcs, command] + list(options) + list(args))
			except:
				return CliHandler.UNKNOWN_ERROR_CODE

		args = arguments.get('ARGS')
		del arguments['ARGS']
		for k, v in arguments.iteritems():
			if v:
				command = k.replace('-', '_')
				break

		if command == '<command>':
			exit(run_vanilla_vcs_command(arguments[command]))

		try:
			getattr(self, command)(options, args)
		except TypeError:
			getattr(self, command)()

	def _repo_type(self):
		with open(os.devnull, 'w') as FNULL:
			if subprocess.call(["git", "rev-parse", "--show-toplevel"], stdout=FNULL, stderr=subprocess.STDOUT) == 0:
				return 'git'
			elif subprocess.call(["hg", "root"], stdout=FNULL, stderr=subprocess.STDOUT) == 0:
				return 'hg'
			else:
				print "fatal: unable to identify version control system to use."
				print "Try manually calling your VCS cli to invoke this command."
				raise IOError

	def help(self):
		print __doc__

	def login(self):
		raise NotImplementedError

	def upload_keys(self):
		raise NotImplementedError

	def generate(self, options, args):
		try:
			vcs = self._repo_type()
			if vcs == 'git':
				repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
			elif vcs == 'hg':
				repo_root = subprocess.check_output(["hg", "root"])
		except IOError:
			sys.stderr.write("koality-generate-yml must be run in a git or hg repo.\n")
			sys.exit(CliHandler.REPO_NOT_FOUND_ERROR_CODE)

		repo_root = " ".join(repo_root.split())
		realpath_repo_root = os.path.realpath(repo_root)
		ConfigCreator().create_config(realpath_repo_root, options)

	def commit(self, options, args):
		def git_commit(options, args):
			exit(subprocess.call(['git', 'commit'] + list(options) + list(args)))

		def hg_commit(options, args):
			with open(os.devnull, 'w') as FNULL:
				subprocess.call(['hg', 'phase', '--draft', '--force', '.'], stdout=FNULL, stderr=subprocess.STDOUT)
				exit(subprocess.call(['hg', 'commit'] + list(options) + list(args)))

		self._run_correct_vcs_function(git_commit, hg_commit, options, args)

	def push(self, options, args):
		def git_push(options, args):
			qualifier = 'for'
			remote = 'origin'
			local_branch = 'HEAD'
			try:
				remote_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
				if remote_branch == 'HEAD':
					exit(subprocess.call(['git', 'push']))
			except subprocess.CalledProcessError as e:
				exit(e.returncode)

			if '-f' in options or '--force' in options:
				qualifier = 'force'
				options = filter(lambda opt: opt != '-f' and opt != '--force', options)

			if len(args) > 0:
				remote = args[0]
			if len(args) > 1:
				local_branch = remote_branch = args[1]
				if ':' in args[1]:
					local_branch, remote_branch = args[1].split(':')

			exit(subprocess.call(['git', 'push'] + options + [remote, '%s:refs/%s/%s' % (local_branch, qualifier, remote_branch)]))

		def hg_push(options, args):
			exit(subprocess.call(['hg', 'push'] + list(options) + list(args)))

		self._run_correct_vcs_function(git_push, hg_push, options, args)

	def _run_correct_vcs_function(self, git_func, hg_func, options, args):
		vcs = self._repo_type()
		if vcs == 'git':
			git_func(options, args)
		elif vcs == 'hg':
			hg_func(options, args)
		else:
			print "fatal: not a git or hg repository."
			exit(CliHandler.UNKNOWN_ERROR_CODE)

	def push_unchecked(self, options, args):
		raise NotImplementedError

	def test(self, options, args):
		raise NotImplementedError

	def update(self):
		raise NotImplementedError

def main():
	opts = []
	args = []
	for i in sys.argv[1:]:
		if i == '-h' or i == '--help' or i == '--version':
			args.append(i)
		elif i.startswith('-'):
			opts.append(i)
		else:
			args.append(i)

	arguments = docopt(__doc__, argv=args, version=koality_cli.__version__)
	CliHandler().handle(opts, arguments)

if __name__ == '__main__':
	main()
