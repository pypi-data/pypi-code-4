from fabric.api import local, settings, lcd, prefix
import os
from datetime import datetime

from .utils import prepare_folder, prepare_virtual_env, \
					local_sed, get_temp_path
from .my_yaml import flatten_dict
from .custom_file import get_custom_file


def get_packages(application_path, config=None, returns_only=None, 
				build_path=None, architecture=None, options=None):
	""" Generator of packages for an application. """
	venv = None
	options = options if options else {}

	# selective return
	if not returns_only:
		returns_only = ['venv', 'app', 'services']
	elif isinstance(returns_only, str):
		returns_only = [returns_only]
	elif not isinstance(returns_only, list):
		raise AttributeError

	# extract config for extra files
	config_extra_files = config.pop("extra_files", [])
	config_applications = config.pop("applications", [])

	# extract version options
	versions_options = options.get("version_options", {})

	if config['type'] == 'configuration':

		# country/product configuration package
		pkg = CountrySettingsPackage(config['name'] + config.get('name_suffix', ""),
									build_path=build_path, version=versions_options.get("app"))
		pkg.prepare(config, config_applications)

	elif config['type'] == 'application':

		# environment package
		if 'environment' in config:
			if config['environment']['type'] == "python":
				venv = PythonEnvironmentPackage(config['environment']['name'] + config.get('name_suffix', ""), 
										application_path, build_path=build_path, architecture=architecture, version=versions_options.get("env"))
				venv.prepare(binary=config['environment'].get('binary', ""),
							requirements=config['environment'].get('requirements', []),
							post_environment_steps=config['environment'].get('post_environment', []), pip_options=options.get("pip_options", ""))
			else:
				raise NotImplementedError("environment type: %s" 
										% config['environment']['type'])

		# main application package
		pkg = ApplicationPackage(config['name']  + config.get('name_suffix', ""), application_path, build_path=build_path,
							environment=venv, version=versions_options.get("app"))
		pkg.prepare(exclude_folders=config.get('exclude_folders', []),
					build_assets_steps=config.get('build_assets', []))

	else:
		raise NotImplementedError

	# extra files attachment
	extra_files_list = {}
	for file_ in config_extra_files:
		file_bin = get_custom_file(file_['type'],
								file_['name'] + config.get('name_suffix', ""),
								file_['template'],
								file_.get('target_path', None),
								file_.get('target_extension', None),
								file_.get('target_is_executable', None),
								options=config)
		pkg.attach_file(file_['name'] + config.get('name_suffix', ""), file_bin)
		extra_files_list[ file_['name'] ] = file_

	# package for each services
	for service in config.get('services', []):
		srv = ServicePackage(service['name'] + config.get('name_suffix', ""), pkg,
							build_path=build_path, version=versions_options.get("service"))
		srv.prepare(binary=service['binary_name'] + config.get('name_suffix', ""),
					binary_file = extra_files_list[ service['binary_name'] ],
					debian_scripts=service.get('debian_scripts', {}),
					env_var=service.get('env_var', {}))

		if "services" in returns_only:
			yield srv

	if venv and "venv" in returns_only:
		yield venv

	if "app" in returns_only:
		yield pkg


class Package(object):
	architecture = "all"

	def __init__(self, name, build_path=None, version=None):
		self.name = name
		self.build_path = build_path if build_path else get_temp_path("build")
		self.full_path = os.path.join(self.build_path, self.name)
		self.version = version if version else ''

		self.dependency_pkg = []
		self.extra_files = {}
		self.settings_package = {}

	def build(self, debs_path, extra_template_dir=None, extra_description=None):
		self.develop(extra_template_dir, extra_description)
		self.pre_package(extra_template_dir)
		self.package(debs_path)

	def develop(self, extra_template_dir=None, extra_description=None):
		self.extra_description = extra_description

		prepare_folder(self.full_path)
		local("rm -rf %s/*" % self.full_path)

		self.pre_build(extra_template_dir=extra_template_dir)

		self.build_extra_files(extra_template_dir=extra_template_dir)
		self.create_deb(extra_template_dir=extra_template_dir)

	def pre_build(self, extra_template_dir=None):
		raise NotImplementedError

	def pre_package(self, extra_template_dir=None):
		pass

	def create_deb(self, extra_template_dir=None):
		""" Create the meta folder for debian package. """
		
		my_cwd = os.path.abspath(os.path.dirname(__file__))
		print "my_cwd: " + my_cwd
		for file_custom in local('ls %s' % os.path.join(my_cwd, "..", "templates", "DEBIAN"),
								 capture=True).split():
			options = {
				'full_package_name': self.full_package_name,
				'architecture':	self.architecture,
				'package_version': self.package_version,
				'description': self.description,
				'dependencies': self.dependencies,
				'package_service_dependencies': self.get_service_dependencies(),
				'settings': self.settings_package,
				'maintainer': 'Arnaud Seilles <arnaud.seilles@gmail.com>',
			}
			template = "DEBIAN/%s" % file_custom

			file_ = get_custom_file('debian', file_custom, template)
			file_.build(self.full_path, 
						options, 
						extra_template_dir=extra_template_dir)

	@property
	def final_deb_name(self): 
		return "%s-%s-%s.deb" % (self.full_package_name, 
							self.package_version, self.architecture)
	def package(self, debs_path):
		prepare_folder(debs_path)

		full_deb= os.path.join(debs_path, self.final_deb_name)

		with settings(warn_only=True):
			local("rm -f %s" % os.path.join(self.full_path, full_deb))
			local('find -L %s -name "*.pyc" -delete' % self.full_path)
			local('find -L %s -name ".git$" -exec rm -r {} \;' % self.full_path)
		local("dpkg-deb --build %s %s" % (self.full_path, full_deb))

	@property
	def full_package_name(self):
		return "dh-%s" % self.name.replace("_", "-")

	@property
	def package_version(self):
		if self.version:
			return self.version

		return "1.0.0"

	@property
	def description(self):
		text = "Package %s (version %s) built on the %s\n" % \
						(self.full_package_name, self.version, datetime.now().isoformat(' '))
		# extended description in a debian pkg can be multilined, must start by at least 1 space.
		if self.extra_description:
			text += "\n".join([ " "+line for line in self.extra_description.split("\n") if line is not ""])

		return text

	@property
	def dependencies(self):
		return [{'name': pkg.full_package_name, 'version': pkg.package_version} for pkg in self.dependency_pkg if pkg]

	def get_extra_file_final_path(self, file_name):
		if file_name not in self.extra_files:
			raise AttributeError

		print self.extra_files

		return os.path.join("/", 
					self.extra_files[file_name].relative_filepath)

	def attach_file(self, name, file_bin):
		self.extra_files[name] = file_bin

	def build_extra_files(self, extra_template_dir=None):
		for key,binary in self.extra_files.iteritems():
			binary.build(self.full_path, 
				self.extra_config,
				extra_template_dir=extra_template_dir)

	@property
	def extra_config(self):
		return {}

	def get_dependencies(self):
		return []

	def get_service_dependencies(self):
		return [self.name]


class ApplicationPackage(Package):
	"""
	If updated, needs to restart all dependent upstart services for this application.
	"""

	def __init__(self, name, application_path,
				build_path=None,
				environment=None,
				version=None):
		self.application_path = application_path
		super(ApplicationPackage, self).__init__(name, build_path=build_path, version=version)
		self.environment = environment

		self.bin_path = os.path.join(self.full_path, "opt", "trebuchet", 
							self.name, "bin")
		self.code_path = os.path.join(self.full_path, "opt", "trebuchet",
							self.name, "code")
		self.dependency_pkg = [environment]

	def prepare(self, exclude_folders=None, build_assets_steps=None, debian_scripts=None):
		self.build_assets_steps = build_assets_steps
		self.exclude_folders = exclude_folders
		if debian_scripts:
			self.settings_package.update({'debian_scripts': debian_scripts})

	def pre_build(self, extra_template_dir=None):		
		prepare_folder(self.code_path)

		local("cp -R %s/* %s" % (self.application_path, self.code_path))
		local("rm -rf %s/.git" % self.code_path)
		for folder in self.exclude_folders:
			local("rm -rf %s/%s" % (self.code_path, folder))

		with lcd(self.code_path):
			local("echo %s > GIT_VERSION" % self.version_from_vcs)

		prefix = ". %s/bin/activate && " % self.environment.working_path if self.environment else ""
		with lcd(self.code_path):
			for step in self.build_assets_steps:
				local(prefix + step)

	@property
	def extra_config(self):
		return {
				'base_template': "base_shell.sh",
				'app_env': self.environment.target_venv if self.environment else "",
				'app_code': os.path.join("/", "opt", "trebuchet", 
						self.name, "code")
			}

	def get_dependencies(self):
		return [self.environment.name] if self.environment else []

	@property
	def version_from_vcs(self):
		if not hasattr(self, '_version_from_vcs'):
			with lcd(self.application_path):
				self._version_from_vcs = local("git rev-parse --verify --short HEAD", capture=True)			

		return self._version_from_vcs


class PythonEnvironmentPackage(Package):
	"""
	If updated, needs to restart all dependent upstart services for this application.
	"""
	def __init__(self, name, application_path, build_path=None, architecture=None, version=None):
		self.application_path = application_path
		super(PythonEnvironmentPackage, self).__init__(name, build_path=build_path, version=version)

		self.working_copy_base = os.path.join("/", "tmp", "trebuchet", "working_copy")
		self.env_path = os.path.join(self.full_path, "opt", "trebuchet", 
							self.name, "env")
		self.venv_bin_path = os.path.join(self.env_path, 'bin')
		self.working_path = os.path.join(self.working_copy_base, 
							self.name, "env")
		self.target_base_path = os.path.join("/", "opt", "trebuchet")
		self.target_venv = os.path.join(self.target_base_path, self.name,
										"env")

		if architecture:
			self.architecture = architecture

	def prepare(self, binary=None, requirements=None,
					post_environment_steps=None,
					pip_options="",
					debian_scripts=None):
		self.binary = binary
		self.requirements = requirements
		self.post_environment_steps = post_environment_steps
		self.pip_options = pip_options
		if debian_scripts:
			self.settings_package.update({'debian_scripts': debian_scripts})

	def pre_build(self, extra_template_dir=None):
		# create a working environment
		prepare_folder(os.path.join(self.working_copy_base))
		prepare_virtual_env(self.working_path, self.binary)

		# install requirements
		for requirement in self.requirements:
			requirement_file = os.path.join(self.application_path, requirement)
			with lcd(self.working_path):
				with prefix(". %s/bin/activate" % self.working_path):
					local('pip install %s -q -r %s' % (self.pip_options, requirement_file))

		# post environment steps
		with lcd(self.working_path):
			for step in self.post_environment_steps:
				with prefix(". %s/bin/activate" % self.working_path):
					local(step)


	def pre_package(self, extra_template_dir=None):
		# copy the working environment to the package location
		prepare_folder(self.env_path)
		local("cp -LR %s/* %s" % (self.working_path, self.env_path))

		# fix symlink
		list_dir = ['bin', 'lib', 'include']
		folder = os.path.join(self.env_path, 'local')
		with settings(warn_only=True):
			if local("test -d %s" % folder).failed:
				with lcd(folder):
					for dir_ in list_dir:
						local("unlink %s" % dir_)
						local("ln -s ../%s %s" % (dir_, dir_))

		# # fix the shebang paths with sed
		with lcd(self.venv_bin_path):
			for script in local('ls', capture=True).split():
				local_sed(
					script,
					self.working_copy_base,
					self.target_base_path
				)
			local("rm -f *.bak")

	@property
	def version_from_vcs(self):
		if not hasattr(self, '_version_from_vcs'):
			with lcd(self.application_path):
				list_files = " ".join(self.requirements)
				self._version_from_vcs = local("git log -n 1 --pretty=format:%%h %s" % list_files, capture=True)			

		return self._version_from_vcs



class ServicePackage(Package):
	"""
	If updated, needs to restart this specific upstart services for this application.
	"""

	def __init__(self, name, application, build_path=None, version=None):
		super(ServicePackage, self).__init__(name, build_path=build_path, version=version)
		self.application = application
		self.dependency_pkg = [application]
		self.env_var = {}

		self.final_service = "dh_" + self.name
		self.controller_service = "%s_controller" % self.final_service
		
	def prepare(self, binary, binary_file, debian_scripts=None, env_var=None):
		self.binary = binary
		self.binary_file = binary_file

		if debian_scripts:
			self.settings_package.update({'debian_scripts': debian_scripts})
		if env_var:
			self.env_var = env_var

	def pre_build(self, extra_template_dir=None):
		# retrieve path to binary from application package
		binary_path = self.application.get_extra_file_final_path(self.binary)

		options = {'executable': binary_path,
				'upstart_worker': self.final_service,
				'package': self.name,
				'name': self.binary,
				'env_var': self.env_var,
				'dependencies': self.get_dependencies()}
		options.update(self.application.extra_config)
		options.update({'base_template': "upstart/base-service.conf"})



		# main upstart file
		upstart_worker = get_custom_file('upstart', self.final_service, 
										self.binary_file['template'])
			
		upstart_worker.build(
				self.full_path,
				options,
				extra_template_dir=extra_template_dir
			)

		# upstart wrappers for all config files (mutliple tasks)
		upstart_ctl = get_custom_file('upstart', self.controller_service, 
										"upstart/controller.conf")	
		upstart_ctl.build(
				self.full_path,
				options,
				extra_template_dir=extra_template_dir
			)

		# executable scripts to control upstart

	def get_dependencies(self):
		deps = [ self.application.name ]
		deps.extend(self.application.get_dependencies())
		return deps

	@property
	def version_from_vcs(self):
		return self.application.version_from_vcs


class CountrySettingsPackage(Package):
	"""
	If updated, needs to restart all upstart services from all applications.
	"""
	template = "config.ini"

	def __init__(self, name, build_path=None, version=None):
		super(CountrySettingsPackage, self).__init__(name, build_path, version=version)
		self.settings_package.update({"use_nginx": True})

	def prepare(self, configuration, config_applications):
		self.config = configuration
		self.config_applications = config_applications
		self.settings_package.update({'country': configuration})

	def pre_build(self, extra_template_dir=None):
		options = self.config
		options.update({'full_name': self.name})

		options.update(self.config_applications)

		# main config file
		main_config = get_custom_file('product', self.name, self.template)	
		main_config.build(
				self.full_path,
				{'options': flatten_dict(options),},
				extra_template_dir=extra_template_dir
			)

	def get_service_dependencies(self):
		return list(self.config_applications.keys())
