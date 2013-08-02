import os.path

from functools import partial

from koality_cli.generators.section_generators.section_generators import TestFactorySectionGenerator


class RubyTestFactorySectionGenerator(TestFactorySectionGenerator):
	def generate_factories_subsection(self):
		factories_script = []
		for index, directory in enumerate(self.dependency_files):
			for test_dir in map(partial(os.path.join, directory), ['Gemfile']):
				if os.path.exists(os.path.join(self.repo_root, test_dir)):
					indicator_dir = directory if directory else '.'
					factories_script.append(self._get_factory_section(
						os.path.join(self.repo_root, indicator_dir),
						directory,
						'find . ' + ' -name "*[tT]est*.rb" | while read rb; do echo -e "- rake test TEST=$rb:\n    path: %s"; done'))
		return factories_script
