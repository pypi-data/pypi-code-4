import os.path

from koality_cli.generators.section_generators.section_generators import CompileScriptsSectionGenerator


class JavaScriptCompileScriptsSectionGenerator(CompileScriptsSectionGenerator):
	def create_scripts_subsection(self):
		compile_scripts = []
		for index, directory in enumerate(self.dependency_files):
			files = os.listdir(directory) if directory else os.listdir('.')
			for name in files:
				if 'Gruntfile' in name:
					compile_scripts.append(self._get_compile_section(
						'%s %d' % ("grunt", index),
						directory,
						"grunt"))
		return compile_scripts
