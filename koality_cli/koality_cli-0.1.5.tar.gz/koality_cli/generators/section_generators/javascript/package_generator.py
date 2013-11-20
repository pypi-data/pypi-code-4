import os

from koality_cli.generators.section_generators.section_generators import PackageSectionGenerator


class JavaScriptPackageSectionGenerator(PackageSectionGenerator):
	def get_install_command(self, directory):
		files = os.listdir(directory) if directory else os.listdir('.')
		for name in files:
			if 'Gruntfile' in name:
				return 'grunt-cli'
		return {}

	def create_dependencies_subsection(self):
		return self.create_dependencies_subsection_helper('js')
