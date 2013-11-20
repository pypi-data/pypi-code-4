from koality_cli.generators.section_generators.section_generators import PackageSectionGenerator


class PythonPackageSectionGenerator(PackageSectionGenerator):
	def get_install_command(self, directory):
		return {'install requirements': '%s/requirements.txt' % directory} if directory else 'install requirements'

	def create_dependencies_subsection(self):
		return self.create_dependencies_subsection_helper('pip')
