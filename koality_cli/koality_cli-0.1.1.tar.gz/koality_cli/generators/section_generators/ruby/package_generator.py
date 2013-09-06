from koality_cli.generators.section_generators.section_generators import PackageSectionGenerator


class RubyPackageSectionGenerator(PackageSectionGenerator):
	def get_install_command(self, directory):
		return {'bundle install': '%s/Gemfile' % directory} if directory else 'bundle install'

	def create_dependencies_subsection(self):
		return self.create_dependencies_subsection_helper('gem')
