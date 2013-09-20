from koality_cli.generators.section_generators.section_generators import PackageSectionGenerator


class JavaPackageSectionGenerator(PackageSectionGenerator):
	def get_install_command(self, directory):
		return

	def create_dependencies_subsection(self):
		return ''
