import os.path
from koality_cli.generators.section_generators.section_generators import TestFactorySectionGenerator


class JavaScriptTestFactorySectionGenerator(TestFactorySectionGenerator):
	def generate_factories_subsection(self):
		return []