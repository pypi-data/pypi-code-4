#!/usr/bin/env python
import os.path
import shutil

import yaml

from koality_cli.generators.config_generators import KoalityConfigTemplateGenerator
from koality_cli.generators.comment_generator import CommentGenerator
from koality_cli.generators.section_generators.section_generators import LanguageSectionGenerator, SetupSectionGenerator, CompileSectionGenerator, TestSectionGenerator
from koality_cli.generators.section_generators.python import PythonPackageSectionGenerator, PythonCompileScriptsSectionGenerator, PythonTestFactorySectionGenerator
from koality_cli.generators.section_generators.ruby import RubyPackageSectionGenerator, RubyCompileScriptsSectionGenerator, RubyTestFactorySectionGenerator
from koality_cli.generators.section_generators.nodejs import NodejsPackageSectionGenerator, NodejsCompileScriptsSectionGenerator, NodejsTestFactorySectionGenerator
from koality_cli.generators.section_generators.java import JavaPackageSectionGenerator, JavaCompileScriptsSectionGenerator, JavaTestFactorySectionGenerator
from koality_cli.generators.section_generators.javascript import JavaScriptPackageSectionGenerator, JavaScriptCompileScriptsSectionGenerator, JavaScriptTestFactorySectionGenerator
from koality_cli.repo_reflector.database_reflector import DatabaseReflector
from koality_cli.repo_reflector.language_reflector import LanguageReflector
from koality_cli.repo_reflector.dependency_reflector import DependencyReflector


class ConfigCreator(object):
	def create_config(self, realpath_repo_root, options):
		generator = self.create_yml_generator(realpath_repo_root, options)
		self.create_yml_file(generator, realpath_repo_root, 'koality.yml')

	def create_yml_generator(self, realpath_repo_root, options):
		language_reflector = LanguageReflector(realpath_repo_root)
		dependency_reflector = DependencyReflector(realpath_repo_root)
		db_reflector = DatabaseReflector(realpath_repo_root)

		extensions = language_reflector.reflect()
		dependency_files = dependency_reflector.reflect()
		databases = db_reflector.reflect()

		language_generator = LanguageSectionGenerator(extensions)
		setup_generator = SetupSectionGenerator(databases, [
			PythonPackageSectionGenerator(dependency_files['python']),
			RubyPackageSectionGenerator(dependency_files['ruby']),
			NodejsPackageSectionGenerator(dependency_files['nodejs']),
			JavaPackageSectionGenerator(dependency_files['java']),
			JavaScriptPackageSectionGenerator(dependency_files['javascript'])
		])
		compile_generator = CompileSectionGenerator([
			PythonCompileScriptsSectionGenerator(dependency_files['python'], realpath_repo_root, options),
			RubyCompileScriptsSectionGenerator(dependency_files['ruby'], realpath_repo_root, options),
			NodejsCompileScriptsSectionGenerator(dependency_files['nodejs'], realpath_repo_root, options),
			JavaCompileScriptsSectionGenerator(dependency_files['java'], realpath_repo_root, options),
			JavaScriptCompileScriptsSectionGenerator(dependency_files['javascript'], realpath_repo_root, options)
		])
		test_generator = TestSectionGenerator([
			PythonTestFactorySectionGenerator(dependency_files['python'], realpath_repo_root, options),
			RubyTestFactorySectionGenerator(dependency_files['ruby'], realpath_repo_root, options),
			NodejsTestFactorySectionGenerator(dependency_files['nodejs'], realpath_repo_root, options),
			JavaTestFactorySectionGenerator(dependency_files['java'], realpath_repo_root, options),
			JavaScriptTestFactorySectionGenerator(dependency_files['javascript'], realpath_repo_root, options)
		])

		koality_config_generator = KoalityConfigTemplateGenerator(language_generator, setup_generator)
		yml_config = koality_config_generator.generate()
		yml_str = ''.join(map(lambda section: yaml.safe_dump(section, width=200, default_flow_style=False), yml_config))
		return CommentGenerator(yml_str, compile_generator, test_generator)


	def create_yml_file(self, generator, realpath_repo_root, filename):
		realpath_repo_root = os.path.realpath(realpath_repo_root)
		koality_config_path = os.path.join(realpath_repo_root, filename)

		if os.path.exists(koality_config_path):
			shutil.move(koality_config_path, koality_config_path + '.bak')
			print "Backed up existing koality configuration file to %s" % (koality_config_path + '.bak')
			print '...'

		with open(koality_config_path, 'w') as f:
			f.write(generator.generate())
		print "Generated a koality configuration file @ %s" % koality_config_path

