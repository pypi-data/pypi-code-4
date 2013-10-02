import os.path

from functools import partial

from koality_cli.generators.section_generators.section_generators import TestFactorySectionGenerator


class NodejsTestFactorySectionGenerator(TestFactorySectionGenerator):
	def generate_factories_subsection(self):
		factories_script = []
		for index, directory in enumerate(self.dependency_files):
			for test_dir in map(partial(os.path.join, directory), ['package.json']):
				if os.path.exists(os.path.join(self.repo_root, test_dir)):
					indicator_dir = directory if directory else '.'
					factories_script.append(self._get_factory_section(test_dir, indicator_dir, 'echo -e "- npm test:\n    path: %s"'))
		return factories_script
