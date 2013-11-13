# -*- coding: utf-8 -*-

from fabric.api import local, settings, lcd, prefix
import os
from datetime import datetime
import fnmatch
import shutil
import copy

from .utils import prepare_folder, prepare_virtual_env, \
                    local_sed, get_temp_path
from .my_yaml import flatten_dict
from .custom_file import get_custom_file, DEBIANCustomFile


def get_packages(application_path, config=None,
                architecture=None, options=None):
    """ Generator of packages for an application. """
    venv = None
    options = options if options else {}

    name_suffix = config.get('name_suffix', "")

    # make deep copy to avoid issue
    new_config = copy.deepcopy(config)
    # extract config for extra files
    config_extra_files = new_config.pop("extra_files", [])
    config_services = new_config.pop("services", [])
    config_applications = new_config.pop("applications", [])
    config_static = new_config.pop('static_files', [])
    config_environment = new_config.pop("environment", None)

    # extract version options
    versions_options = options.pop("version_options", {})

    # environment package
    # TODO clean arguments
    # TODO use factory for type of environment
    if config_environment:
        if config_environment['type'] == "python":
            venv = PythonEnvironmentPackage(config_environment['name'] + name_suffix, application_path,
                                    architecture=architecture,
                                    version=versions_options.get("env"))
            venv.prepare(binary=config_environment.get('binary', ""),
                        requirements=config_environment.get('requirements', []),
                        debian_scripts=config_environment.get('debian_scripts', {'postinst': [], 'preinst':[], 'prerm':[]}),
                        post_environment_steps=config_environment.get('post_environment', []),
                        pip_options=options.get("pip_options", ""))
        else:
            raise NotImplementedError("environment type: %s"
                                    % config_environment['type'])

    # main application package
    # TODO clean arguments
    if config.get('type') == "application":
        pkg = ApplicationPackage(config['name']  + name_suffix, application_path,
                        environment=venv, version=versions_options.get("app"))
    elif config.get('type') == "configuration":
        pkg = ConfigurationPackage(config['name']  + name_suffix, application_path,
                        environment=venv, version=versions_options.get("app"))
    else:
        raise NotImplementedError("package type: %s" % config.get('type'))

    pkg.prepare(exclude_folders=config.pop('exclude_folders', []),
                build_assets_steps=config.pop('build_assets', []),
                debian_scripts=config.pop('debian_scripts', {'postinst': [], 'preinst':[], 'prerm':[]}),
                configuration=config,
                config_applications=config_applications)


    # extra files attachment
    # TODO clean arguments
    # TODO keep options=config?
    extra_files_list = {}
    for file_ in config_extra_files:
        file_bin = get_custom_file(file_['type'],
                                file_['name'] + name_suffix,
                                file_['template'],
                                file_.get('target_path', None),
                                file_.get('target_extension', None),
                                file_.get('target_is_executable', None),
                                file_.get('target_filename', None),
                                file_['name'],
                                options=config)
        pkg.attach_file(file_['name'] + config.get('name_suffix', ""), file_bin)
        extra_files_list[ file_['name'] ] = file_

    # package for each services
    # TODO link to the extra file created previously
    for service in config_services:
        srv = ServicePackage(service['name'] + name_suffix, pkg,
                            version=versions_options.get("service"))
        srv.prepare(binary=service['binary_name'] + name_suffix,
                    binary_file = extra_files_list[ service['binary_name'] ],
                    debian_scripts=service.get('debian_scripts', {'postinst': [], 'preinst':[], 'prerm':[]}),
                    env_var=service.get('env_var', {}))
        yield srv

    if venv: yield venv
    yield pkg

    for staticfileconf in config_static:
        static = StaticPackage(staticfileconf['name']+name_suffix, pkg,
                               version=versions_options.get("static_files"))
        static.prepare(folders = staticfileconf.pop('folders'),
                    debian_scripts=staticfileconf.pop('debian_scripts', {'postinst': [], 'preinst':[], 'prerm':[]}))
        yield static


class Package(object):
    architecture = "all"

    def __init__(self, name, path, version=None, build_path=None, ):
        self.name = name
        self.version = version if version else ''
        self.path = path

        self.dependency_pkg = []
        self.extra_files = {}
        self.settings_package = {}
        self.template_options = {}
        self.debian_scripts = {}

        self.build_path = build_path if build_path else os.path.join(get_temp_path("build"), self.name)

    def build(self, debs_path, extra_description=None):
        self.develop(extra_description)
        self.package(debs_path, self.build_path)

    def develop(self, extra_description=None):
        self.prepare_build_folder(self.build_path)
        self.pre_build(self.build_path)
        self.build_extra_files(self.build_path)
        self.create_deb(self.build_path, extra_description)

    def prepare_build_folder(self, build_path):
        prepare_folder(build_path)
        local("rm -rf %s/*" % build_path)

    def pre_build(self, build_path):
        raise NotImplementedError

    def create_deb(self, build_path, extra_description=None):
        """ Create the meta folder for debian package. """
        options = {
                'full_package_name':    self.full_package_name,
                'architecture':         self.architecture,
                'package_version':      self.package_version,
                'description':          self.get_description(extra_description),
                'dependencies':         self.dependencies,
                'package_service_dependencies': self.get_service_dependencies(),
                'settings':             self.settings_package,
                'debian_scripts':       self.debian_scripts,
                'maintainer':           'Arnaud Seilles <arnaud.seilles@gmail.com>',
            }
        options.update(self.template_options)

        my_cwd = os.path.abspath(os.path.dirname(__file__))
        for file_custom in local('ls %s' % os.path.join(my_cwd, "..", "templates", "DEBIAN"),
                                 capture=True).split():
            file_ = DEBIANCustomFile(file_custom, os.path.join("DEBIAN", file_custom))
            file_.build(build_path,
                        options=options,
                        extra_template_dir=self.path)

    @property
    def final_deb_name(self):
        return "%s-%s-%s.deb" % (self.full_package_name,
                            self.package_version, self.architecture)

    def package(self, debs_path, build_path):
        prepare_folder(debs_path)

        full_deb= os.path.join(debs_path, self.final_deb_name)

        with settings(warn_only=True):
            local("rm -f %s" % os.path.join(build_path, full_deb))
            local('find -L %s -name "*.pyc" -delete' % build_path)
            local('find -L %s -name ".git$" -exec rm -r {} \;' % build_path)
        local("dpkg-deb --build %s %s" % (build_path, full_deb))

    @property
    def full_package_name(self):
        return "dh-%s" % self.name.replace("_", "-")

    @property
    def package_version(self):
        if self.version:
            return self.version

        return "1.0.0"

    def get_description(self, extra_description=""):
        text = "Package %s (version %s) built on the %s\n" % \
                        (self.full_package_name, self.version, datetime.now().isoformat(' '))
        # extended description in a debian pkg can be multilined, must start by at least 1 space.
        if extra_description:
            text += "\n".join([ " "+line for line in extra_description.split("\n") if line is not ""])

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

    def build_extra_files(self, build_path):
        options = {}
        options.update(self.extra_config)
        options.update(self.template_options)

        for key,binary in self.extra_files.iteritems():
            binary.build(build_path,
                options,
                extra_template_dir=self.path)

    @property
    def extra_config(self):
        return {}

    def get_dependencies(self):
        return []

    def get_service_dependencies(self):
        if not hasattr(self, 'config_applications') or self.config_applications is None:
            return [self.name]
        if self.config_applications == []:
            return {}
        return list(self.config_applications.keys())


class ApplicationPackage(Package):
    """
    If updated, needs to restart all dependent upstart services for this application.
    """

    def __init__(self, name, application_path,
                environment=None,
                version=None):
        self.application_path = application_path
        super(ApplicationPackage, self).__init__(name, application_path, version=version)

        self.environment = environment
        self.dependency_pkg = [environment]

        self.relative_final_path = os.path.join("opt", "trebuchet", self.name, "code")

    def prepare(self, exclude_folders=None, build_assets_steps=None, debian_scripts=None,
                configuration=None, config_applications=None):
        self.build_assets_steps = build_assets_steps
        self.exclude_folders = exclude_folders
        self.debian_scripts = debian_scripts
        self.config = configuration
        self.config_applications = config_applications

    def pre_build(self, build_path):
        code_path = os.path.join(build_path, self.relative_final_path)
        
        prepare_folder(code_path)

        self._prepare_code_path(build_path, code_path)
        self._prepare_folders(build_path, code_path)
        self._run_build_asset_steps(build_path, code_path)
        self._add_extra_files_config(build_path, code_path)

    def _prepare_code_path(self, build_path, code_path):
        local("cp -R %s/* %s" % (self.application_path, code_path))

    def _prepare_folders(self, build_path, code_path):
        for folder in self.exclude_folders:
            local("rm -rf %s/%s" % (code_path, folder))

        local("rm -rf %s/.git" % code_path)
        with lcd(code_path):
            local("echo %s > GIT_VERSION" % self.version_from_vcs)

    def _run_build_asset_steps(self, build_path, code_path):
        prefix = ". %s/bin/activate && " % self.environment.working_path if self.environment else ""
        with lcd(code_path):
            for step in self.build_assets_steps:
                local(prefix + step)
        self.template_options['is_python'] = isinstance(self.environment, PythonEnvironmentPackage)
        self.template_options['pyfiles_path'] = os.path.join("/", self.relative_final_path)

    def _add_extra_files_config(self, build_path, code_path):
        # from configuration
        options = self.config
        options.update({'full_name': self.name})
        options.update(self.config_applications)
        # add extrafiles information (maiden_name is the un-suffixed name)
        options['extra_files'] = {}
        for key,binary in self.extra_files.iteritems():
            options['extra_files'][binary.unsuffixed_name] = binary.relative_filepath
        self.template_options.update({'options': flatten_dict(options),})

    @property
    def extra_config(self):
        return {
                'base_template': "base_shell.sh",
                'app_env': self.environment.target_venv if self.environment else "",
                'app_code': os.path.join("/", self.relative_final_path)
            }

    def get_dependencies(self):
        return [self.environment.name] if self.environment else []

    @property
    def version_from_vcs(self):
        if not hasattr(self, '_version_from_vcs'):
            with lcd(self.application_path):
                self._version_from_vcs = local("git rev-parse --verify --short HEAD || hg log -r -1 --template \"{short(node)}\\n\"", capture=True)

        return self._version_from_vcs


class PythonEnvironmentPackage(Package):
    """
    If updated, needs to restart all dependent upstart services for this application.
    """
    def __init__(self, name, application_path, architecture=None, version=None):
        self.application_path = application_path
        super(PythonEnvironmentPackage, self).__init__(name, application_path, version=version)

        self.working_path = os.path.join("/", "tmp", "trebuchet", "working_copy", self.name, "env")

        self.relative_final_path = os.path.join("opt", "trebuchet", self.name, "env")
        self.target_venv = os.path.join("/", self.relative_final_path)

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
            self.debian_scripts = debian_scripts

    def pre_build(self, build_path):
        env_path = os.path.join(build_path, self.relative_final_path)
        venv_bin_path = os.path.join(env_path, 'bin')

        # create a working environment
        prepare_virtual_env(self.working_path, self.binary)

        # install requirements
        for requirement in self.requirements:
            requirement_file = os.path.join(self.application_path, requirement)
            with lcd(self.working_path):
                with prefix(". %s/bin/activate" % self.working_path):
                    local('pip install %s --install-option --no-compile --install-option -O0 -q -r %s' % (self.pip_options, requirement_file))

        # post environment steps
        with lcd(self.working_path):
            for step in self.post_environment_steps:
                with prefix(". %s/bin/activate" % self.working_path):
                    local(step)
        self.template_options['is_python'] = True
        self.template_options['pyfiles_path'] = self.target_venv

        # copy the working environment to the package location
        prepare_folder(env_path)
        local("cp -LR %s/* %s" % (self.working_path, env_path))

        # fix symlink
        list_dir = ['bin', 'lib', 'include']
        folder = os.path.join(env_path, 'local')
        with settings(warn_only=True):
            if local("test -d %s" % folder).failed:
                with lcd(folder):
                    for dir_ in list_dir:
                        local("unlink %s" % dir_)
                        local("ln -s ../%s %s" % (dir_, dir_))

        # # fix the shebang paths with sed
        with lcd(venv_bin_path):
            for script in local('ls', capture=True).split():
                local_sed(
                    script,
                    self.working_path,
                    self.target_venv
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

    def __init__(self, name, application, version=None):
        super(ServicePackage, self).__init__(name, application.path, version=version)
        self.application = application
        self.dependency_pkg = [application]
        self.env_var = {}

        self.final_service = "dh_" + self.name
        self.controller_service = "%s_controller" % self.final_service

    def prepare(self, binary, binary_file, debian_scripts=None, env_var=None):
        self.binary = binary
        self.binary_file = binary_file

        if debian_scripts:
            self.debian_scripts = debian_scripts
        if env_var:
            self.env_var = env_var

    def pre_build(self, build_path):
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
                build_path,
                options,
                extra_template_dir=self.path
            )

        # upstart wrappers for all config files (mutliple tasks)
        upstart_ctl = get_custom_file('upstart', self.controller_service,
                                        "upstart/controller.conf")
        upstart_ctl.build(
                build_path,
                options,
                extra_template_dir=self.path
            )

    def get_dependencies(self):
        deps = [ self.application.name ]
        deps.extend(self.application.get_dependencies())
        return deps

    @property
    def version_from_vcs(self):
        return self.application.version_from_vcs

class ConfigurationPackage(ApplicationPackage):
    """
    If updated, needs to restart all dependent upstart services for this application.
    """

    def __init__(self, name, application_path,
                environment=None,
                version=None):
        self.application_path = application_path
        super(ConfigurationPackage, self).__init__(name, application_path, environment=None, version=version)
        self.relative_final_path = ""

    def _prepare_code_path(self, build_path, code_path):
        pass


class StaticPackage(Package):
    def __init__(self,
                 name,
                 application,
                 version=None):
        self.application = application
        super(StaticPackage, self).__init__(name, application.path, version=version)
        self.relative_final_path = os.path.join("opt", "trebuchet", self.name, "static")

    def prepare(self, folders, debian_scripts=None):
        self.folders = folders
        if debian_scripts:
            self.debian_scripts = debian_scripts

    def pre_build(self, build_path):
        for folder in self.folders:

            def exclude_and_include(path, names):
                names = set(names)
                if 'includes' in folder:
                    for include in folder['includes']:
                        names.difference_update(
                            set(fnmatch.filter(list(names), include)))
                if 'excludes' in folder:
                    for exclude in folder['excludes']:
                        names = set(fnmatch.filter(list(names), exclude))
                return list(names)

            source = os.path.join(self.application.build_path, self.application.relative_final_path, folder['path'])

            if self.application.relative_final_path == "":
                destination = os.path.join(build_path, folder['path'])
            else:
                destination = os.path.join(build_path, self.relative_final_path, folder['path'])

            shutil.copytree(source, destination, ignore=exclude_and_include)
