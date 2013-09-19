import os.path

from functools import partial

from koality_cli.generators.section_generators.section_generators import TestFactorySectionGenerator


class PythonTestFactorySectionGenerator(TestFactorySectionGenerator):
	def generate_factories_subsection(self):
		django_scripts = self._django_factory()
		if django_scripts:
			return django_scripts
		default_scripts = self._default_factory()
		return default_scripts

	def _default_factory(self):
		factories_script = []
		for index, directory in enumerate(self.dependency_files):
			for test_dir in map(partial(os.path.join, directory), ['setup.py']):
				if os.path.exists(os.path.join(self.repo_root, test_dir)):
					indicator_dir = directory if directory else '.'
					factories_script.append(self._get_factory_section(
						os.path.join(self.repo_root, indicator_dir),
						directory,
						'find . -name "*[tT]est*.py" | while read py; do echo -e "- nosetests -sv $py:\n    path: %s"; done'))
		return factories_script

	def _django_factory(self):
		factories_script = []
		for index, directory in enumerate(self.dependency_files):
			for test_dir in map(partial(os.path.join, directory), ['manage.py']):
				managepy_path = os.path.join(self.repo_root, test_dir)
				if os.path.exists(managepy_path):
					if not self._is_django_managepy(managepy_path):
						continue
					indicator_dir = directory if directory else '.'
					py = r"import sys; print map(lambda module: {module: {'path': '%s', 'script': 'python manage.py test --noinput ' + module}}, filter(lambda module: bool(module), set(map(lambda line: '.'.join(line.lstrip('./').split('/')[:-1]), sys.stdin.read().split('\n')))))"
					factories_script.append(self._get_factory_section(
						os.path.join(self.repo_root, indicator_dir),
						directory,
						'find . -name "*[tT]est*.py" | python -c "%s"' % py))
		return factories_script

	def _is_django_managepy(self, managepy_path):
		with open(managepy_path) as f:
			for line in f.readlines():
				if "django" in line:
					return True
		return False
