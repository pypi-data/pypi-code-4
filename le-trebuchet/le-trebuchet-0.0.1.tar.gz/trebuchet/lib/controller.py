import itertools

from .package import get_packages
from .my_yaml import load_yaml_config, print_pretty, get_yaml_config
from .callbacks import do_web_callback



def _get_all_packages(project, build_path=None, architecture=None, options=None):
    """
    Generator of packages to be built.
    """
    configs = get_yaml_config(project.config_file)
    pkg_list = []

    # Retrieve all packages from the configuration file.
    for config in configs:
        pkg = get_packages(project.full_path,
                        config=config,
                        build_path=build_path,
                        architecture=architecture,
                        options=options)
        pkg_list.append(pkg)

    # yield the packages again
    for pkg in itertools.chain(*pkg_list):
        yield pkg


def check_config(project):
    """
    """
    pkg_list = [ pkg.full_package_name for pkg in _get_all_packages(project) ]
    print "Packages to be built: " + ",".join(pkg_list)


def build_app(project, prepare, package, version_options=None):
    """
    Locally build the application packages
    """
    pkg_list = []

    for pkg in _get_all_packages(project,
                            build_path=prepare.build_path, 
                            architecture=prepare.architecture,
                            options={"pip_options": prepare.pip_options, 
                                    "version_options": version_options}):
        pkg.build(package.debs_path, 
                extra_template_dir=project.full_path, 
                extra_description=prepare.extra_description)
        pkg_list.append(pkg.final_deb_name)

        if package.web_callback_url:
            do_web_callback(package.web_callback_url, pkg)

    print pkg_list


def develop_app(project, prepare, version_options=None):
    """
    Locally prepare the working copy to be built for the application packages
    """
    pkg_list = []

    for pkg in _get_all_packages(project,
                            build_path=prepare.build_path, 
                            architecture=prepare.architecture,
                            options={"pip_options": prepare.pip_options, 
                                    "version_options": version_options}):
        pkg.develop(extra_template_dir=project.full_path,
                extra_description=prepare.extra_description)
        pkg_list.append(pkg.final_deb_name)

    print pkg_list


def print_build_details(project, versions):
    """
    Print some details related to the build.
    """
    print "config file to use: " + project.config_file
    print "project to use: " + project.full_path
    print versions