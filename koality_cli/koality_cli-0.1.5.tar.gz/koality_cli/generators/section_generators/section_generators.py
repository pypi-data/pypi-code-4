from itertools import chain


class SectionGenerator(object):
	def generate(self):
		raise NotImplementedError("Subclasses should override this!")


class LanguageSectionGenerator(SectionGenerator):
	LANG_MAPPINGS = {
		'.py': {'python': 2.7},
		'.rb': {'ruby': '1.9.3'},
		'.js': {'nodejs': '0.10.13'},  # Assume you use node
		'.coffee': {'nodejs': '0.10.13'},  # Assume you use node
		'.java': {'jvm': 1.6},
		'.scala': {'jvm': 1.6},
		'.clj': {'jvm': 1.6}
	}

	def __init__(self, extensions):
		self.extensions = extensions

	def generate(self):
		return self._create_language_section()

	def _create_language_section(self):
		language_mapping = {}
		for ext in self.extensions:
			language_mapping.update(self.LANG_MAPPINGS[ext])
		return language_mapping


class SetupSectionGenerator(SectionGenerator):
	def __init__(self, databases, package_generators):
		super(SetupSectionGenerator, self).__init__()
		self.databases = databases
		self.package_generators = package_generators

	def get_compile_script(self):
		raise NotImplementedError("Subclasses should override this!")

	def generate(self):
		setup_section = []
		package_section = self._create_package_section()
		db_section = self._create_databases_section()
		if package_section['packages']:
			setup_section.append(package_section)
		if db_section['databases']:
			setup_section.append(db_section)
		return setup_section

	def _create_package_section(self):
		package_section = []
		for gen in self.package_generators:
			section = gen.create_packages_section()
			if section:
				package_section.extend(section)
		return {'packages': package_section}

	def _create_databases_section(self):
		def create_databases_subsection():
			databases = []
			for db in self.databases:
				db_settings = {}
				db_settings[db] = [{
					'name': 'test_db',
					'username': 'test_user'
				}]
				databases.append(db_settings)
			return databases

		return {'databases': create_databases_subsection()}


class PackageSectionGenerator(SectionGenerator):
	def __init__(self, dependency_files):
		super(PackageSectionGenerator, self).__init__()
		self.dependency_files = dependency_files

	def generate(self):
		return self.create_packages_section()

	def get_install_command(self, directory):
		raise NotImplementedError("Subclasses should override this!")

	def create_dependencies_subsection(self):
		raise NotImplementedError("Subclasses should override this!")

	def create_dependencies_subsection_helper(self, dependency_header):
		dependencies = {}
		for directory in self.dependency_files:
			install_command = self.get_install_command(directory)
			if install_command:
				dependencies.setdefault(dependency_header, []).append(install_command)
		return [dependencies] if dependencies else []

	def create_packages_section(self):
		dependencies_subsection = self.create_dependencies_subsection()
		if dependencies_subsection:
			return dependencies_subsection
		return None


class CompileSectionGenerator(SectionGenerator):
	def __init__(self, scripts_section_generators):
		super(CompileSectionGenerator, self).__init__()
		self.scripts_section_generators = scripts_section_generators

	def generate(self):
		compile_section = {}
		scripts = list(chain.from_iterable([gen.generate() for gen in self.scripts_section_generators]))
		compile_section['scripts'] = scripts
		return compile_section


class CompileScriptsSectionGenerator(SectionGenerator):
	def __init__(self, dependency_files, repo_root, options):
		super(CompileScriptsSectionGenerator, self).__init__()
		self.dependency_files = dependency_files
		self.repo_root = repo_root
		self.options = options

	def _get_compile_section(self, name, directory, install_script):
		inner = {'script': install_script}
		if directory:
			inner['path'] = directory
		return {name: inner}

	def generate(self):
		return self.create_scripts_subsection()

	def create_scripts_subsection(self):
		raise NotImplementedError("Subclasses should override this!")


class TestSectionGenerator(SectionGenerator):
	def __init__(self, factory_section_generators):
		super(TestSectionGenerator, self).__init__()
		self.factory_section_generators = factory_section_generators

	def generate(self):
		test_section = {}
		test_section['factories'] = list(chain.from_iterable([gen.generate() for gen in self.factory_section_generators]))
		return test_section


class TestFactorySectionGenerator(SectionGenerator):
	def __init__(self, dependency_files, repo_root, options):
		super(TestFactorySectionGenerator, self).__init__()
		self.dependency_files = dependency_files
		self.repo_root = repo_root
		self.options = options

	def _get_factory_section(self, test_dir, directory, test_factory_script):
		assert isinstance(test_factory_script, str)
		directory = directory if directory else '.'
		inner = {'script': [test_factory_script % directory]}
		if directory:
			inner['path'] = directory
		section_name = 'factory %s' % test_dir[len(self.repo_root):].lstrip('/') if test_dir.startswith(self.repo_root) else test_dir
		return {section_name: inner}

	def generate(self):
		return self.generate_factories_subsection()

	def generate_factories_subsection(self):
		raise NotImplementedError("Subclasses should override this!")
