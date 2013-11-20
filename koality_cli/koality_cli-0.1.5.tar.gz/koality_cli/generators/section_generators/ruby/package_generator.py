import os

from koality_cli.generators.section_generators.section_generators import PackageSectionGenerator


class RubyPackageSectionGenerator(PackageSectionGenerator):
	def get_install_command(self, directory):
		if not directory:
			return 'bundle install'
		
		files = os.listdir(directory)
		if 'Gemfile' in files:
			return {'bundle install': '%s/Gemfile' % directory}
		return {}

	def create_dependencies_subsection(self):
		return self.create_dependencies_subsection_helper('gem')
