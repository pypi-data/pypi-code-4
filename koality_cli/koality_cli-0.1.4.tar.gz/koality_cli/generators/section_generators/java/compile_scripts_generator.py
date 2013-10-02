import os.path

from koality_cli.generators.section_generators.section_generators import CompileScriptsSectionGenerator


class JavaCompileScriptsSectionGenerator(CompileScriptsSectionGenerator):
	def create_scripts_subsection(self):
		compile_scripts = []
		for index, directory in enumerate(self.dependency_files):
			if os.path.exists(os.path.join(self.repo_root, directory, "pom.xml")):
				compile_scripts.append(self._get_compile_section(
					'%s %d' % ("mvn compile", index),
					directory,
					"mvn compile"))
		return compile_scripts
