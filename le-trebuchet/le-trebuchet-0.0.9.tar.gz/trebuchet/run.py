#!/usr/bin/env python

"""Trebuchet.

Build debian packages out of a configuration file.
Lint command will check the configuration file and output the list of packages to be built.

Usage:
    trebuchet build <config_file> [--output DEBS_PATH] [--build BUILD_PATH] [--arch ARCH] [--pip-options PIP-OPTIONS] [--app-version APP_VERSION] [--env-version ENV_VERSION] [--service-version SERVICE_VERSION] [--static-version STATIC_VERSION] [--dry-run] [--web-callback URL] [--extra-description MESSAGE]
    trebuchet develop <config_file> [--build BUILD_PATH] [--arch ARCH] [--pip-options PIP-OPTIONS] [--app-version APP_VERSION] [--env-version ENV_VERSION] [--service-version SERVICE_VERSION] [--extra-description MESSAGE]
    trebuchet lint <config_file>
    trebuchet -h | --help
    trebuchet --version

Options:
    -h --help               Show this screen.
    --version               Show version.
    --output DEBS_PATH      Path for the packages to be created. Default to current working directory.
    --build BUILD_PATH      Path for temporary build.
    --arch ARCH             Architecture to use to build lib packages (i386 or amd64).
    --pip-options PIP-OPTIONS   Extra options passed to `pip install` like `--index-url http://pypi.travis-ci.org/simple --extra-index-url http://pypi.python.org/simple`. [default: ]
    --app-version APP_VERSION Option for versioning of the application/configuration package. Default is "1.0.0".
    --env-version ENV_VERSION Option for versioning of the environment package. Default is "1.0.0".
    --service-version SERVICE_VERSION Option for versioning of the service packages. Default is "1.0.0".
    --static-version STATIC_VERSION Option for versioning of the static files packages. Default is "1.0.0".
    --dry-run               Do NOT actually build the packages. Only output the configuration.
    --web-callback URL      Make a HTTP POST request to URL after each package is built with some information related to the build.
    --extra-description MESSAGE Extra description for all the packages built.

The most commonly used git commands are:
   build        Prepare project and build packages out of it.
   develop      Prepare project for build.
   lint         Validate the missile configuration and output the list of packages to be built.

"""
from docopt import docopt
import sys

from lib import get_version
from lib.controller import check_config, build_app, develop_app, print_build_details
from parser import parse_version, parse_project, parse_prepare, parse_package


__version__ = get_version()


def main():
    """
    Main function to handle the arguments and all.
    """

    arguments = docopt(__doc__, version=__version__)

    project_config = parse_project(arguments)

    # We are trying to build the packages
    if arguments['build']:

        # parse the arguments into configuration objects.
        package_config = parse_package(arguments)
        prepare_config = parse_prepare(arguments)
        versions = parse_version(arguments)

        # dry run will just print some details.
        if arguments.get("--dry-run"):
            print_build_details(project_config, versions)
            sys.exit(0)

        build_app(project_config,
            prepare_config,
            package_config,
            version_options=versions)

    # We are trying to prepare the project for development (prior packaging)
    elif arguments['develop']:

        # parse the arguments into configuration objects.
        prepare_config = parse_prepare(arguments)
        versions = parse_version(arguments)

        develop_app(project_config,
            prepare_config,
            version_options=versions)

    # We check if the configuration file is ok.
    elif arguments['lint']:

        pkg_list = check_config(project_config)
        print "Packages to be built: " + ",".join(pkg_list)


if __name__ == '__main__':
    main()
