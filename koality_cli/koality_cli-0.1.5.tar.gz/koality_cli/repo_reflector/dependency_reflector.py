import collections
import os

from reflector import Reflector


class DependencyReflector(Reflector):
	def reflect(self):
		language_directory_mapping = collections.defaultdict(set)
		for root, dirs, files in os.walk(self.repo_dir):
			if 'node_modules' in root:
				continue
			if 'gem' in dirs:
				dirs.remove('gem')
			if 'gems' in dirs:
				dirs.remove('gems')
			if 'plugin' in dirs:
				dirs.remove('plugin')
			if 'plugins' in dirs:
				dirs.remove('plugins')
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
		elif name.endswith('requirements.txt'):
			return 'python'
		elif name == 'Gemfile' or name == 'Rakefile':
			return 'ruby'
		elif name == 'pom.xml':
			return 'java'
		elif 'Gruntfile' in name:
			return 'javascript'

	def _is_package_manager_file(self, name):
		return name in ['package.json', 'Gemfile', 'Rakefile', 'pom.xml'] or name.endswith('requirements.txt') or 'Gruntfile' in name
