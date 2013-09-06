import collections
import os

from reflector import Reflector


class DependencyReflector(Reflector):
	def reflect(self):
		language_directory_mapping = collections.defaultdict(set)
		for root, dirs, files in os.walk(self.repo_dir):
			if 'node_modules' in root:
				continue
			if '.git' in dirs:
				dirs.remove('.git')
			if '.git' in files:
				del dirs[:]
			else:
				for name in files:
					if self._is_package_manager_file(name):
						lang = self._get_language_from_file(name)
						language_directory_mapping[lang].add(self.repo_relative(root))
		return language_directory_mapping

	def _get_language_from_file(self, name):
		if name == 'package.json':
			return 'nodejs'
		elif name == 'requirements.txt':
			return 'python'
		elif name == 'Gemfile':
			return 'ruby'
		elif name == 'pom.xml':
			return 'java'

	def _is_package_manager_file(self, name):
		return name in [
			'package.json',
			'requirements.txt',
			'Gemfile',
			'pom.xml'
		]
