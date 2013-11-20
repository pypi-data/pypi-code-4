import os.path
import subprocess

from functools import partial

from koality_cli.generators.section_generators.section_generators import TestFactorySectionGenerator


class RubyTestFactorySectionGenerator(TestFactorySectionGenerator):
	def generate_factories_subsection(self):
		factories_script = []

		rake_commands = []
		try:
			raket_output = subprocess.check_output(["bundle", "exec", "rake", "-T"], stderr=subprocess.STDOUT)
			rake_commands = [parts.split()[1] for parts in raket_output.strip().split('\n')]
		except (subprocess.CalledProcessError, OSError) as e:
			if '--debug' in self.options:
				print ""
				print "output:"
				print e.output

		if not rake_commands:
			try:
				raket_output = subprocess.check_output(["rake", "-T"], stderr=subprocess.STDOUT)
				rake_commands = [parts.split()[1] for parts in raket_output.strip().split('\n')]
			except (subprocess.CalledProcessError, OSError) as e:
				print ""
				print "Unable to find rake commands."
				print "If this is a ruby repository, this means we've failed to infer test section. You'll need to manually edit this part of the configuration yourself."
				if '--debug' in self.options:
					print ""
					print "output:"
					print e.output
				print ""


		# try with bundler
		for index, directory in enumerate(self.dependency_files):
			for indicator_file in map(partial(os.path.join, directory), ['Gemfile']):
				if os.path.exists(os.path.join(self.repo_root, indicator_file)):
					indicator_dir = directory if directory else '.'

					# normal tests
					if 'test' in rake_commands:
						factories_script.append(self._get_factory_section(
							os.path.join(self.repo_root, indicator_dir),
							directory,
							'find . -name "*test*.rb" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- bundle exec rake test TEST=$rb:\n    path: %s"; done'))

					# spec tests
					if 'spec' in rake_commands:
						factories_script.append(self._get_factory_section(
							os.path.join(self.repo_root, indicator_dir),
							directory,
							'find . -name "*spec*.rb" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- bundle exec rake spec SPEC=$rb:\n    path: %s"; done'))


					# cucumber tests
					if 'cucumber' in rake_commands:
						factories_script.append(self._get_factory_section(
							os.path.join(self.repo_root, indicator_dir),
							directory,
							'find . -name "*.feature" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- bundle exec rake cucumber FEATURE=$rb:\n    path: %s"; done'))
					elif 'features' in rake_commands:
						factories_script.append(self._get_factory_section(
							os.path.join(self.repo_root, indicator_dir),
							directory,
							'find . -name "*.feature" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- bundle exec rake features FEATURE=$rb:\n    path: %s"; done'))

		if not factories_script:
			# try with just rake
			for index, directory in enumerate(self.dependency_files):
				for indicator_file in map(partial(os.path.join, directory), ['Rakefile']):
					if os.path.exists(os.path.join(self.repo_root, indicator_file)):
						indicator_dir = directory if directory else '.'

						# normal tests
						if 'test' in rake_commands:
							factories_script.append(self._get_factory_section(
								os.path.join(self.repo_root, indicator_dir),
								directory,
								'find . -name "*test*.rb" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- rake test TEST=$rb:\n    path: %s"; done'))
						
						# spec tests
						if 'spec' in rake_commands:
							factories_script.append(self._get_factory_section(
								os.path.join(self.repo_root, indicator_dir),
								directory,
								'find . -name "*spec*.rb" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- rake spec SPEC=$rb:\n    path: %s"; done'))


						# cucumber tests
						if 'cucumber' in rake_commands:
							factories_script.append(self._get_factory_section(
								os.path.join(self.repo_root, indicator_dir),
								directory,
								'find . -name "*.feature" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- rake cucumber FEATURE=$rb:\n    path: %s"; done'))
						elif 'features' in rake_commands:
							factories_script.append(self._get_factory_section(
								os.path.join(self.repo_root, indicator_dir),
								directory,
								'find . -name "*.feature" -not -path "*/gem*/*" -and -not -path "*/plugin*/*" | while read rb; do echo -e "- rake features FEATURE=$rb:\n    path: %s"; done'))


		return factories_script
