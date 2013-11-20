from koality_cli.generators.section_generators.section_generators import PackageSectionGenerator


class NodejsPackageSectionGenerator(PackageSectionGenerator):
	def get_install_command(self, directory):
		return {'npm install': directory} if directory else 'npm install'

	def create_dependencies_subsection(self):
		return self.create_dependencies_subsection_helper('npm')
