#!/usr/bin/env python
"""Bootstrap python packages with sane defaults

Features include:

* Generates .gitignore, AUTHORS, CHANGELOG,
  LICENSE (BSD simplified by default), MANIFEST.in, README.md,
  requirements.txt, setup.py, tests.py and tox.ini.
* Sets your name, github username, package name in the templates by
  reading a config that should be located @ ~/.config/pkgtmpl.ini.
* Optional: Add Travis CI status and twitter account to the readme
* Sets your name and year in the copyright notice of the license file

"""
from __future__ import print_function
import argparse
import os
import subprocess
import sys
from datetime import datetime
import jinja2

try:
    import configparser # py3
except ImportError:
    import ConfigParser as configparser # py2

def expand_path(path):
    return os.path.abspath(os.path.expanduser(path))

DEFAULT_CONFIG_PATH = expand_path('~/.config/pkgtmpl.ini')

GENERAL_CONFIG_SECTION = 'general'

FILENAMES = {
    'python': (
        '.gitignore',
        '.travis.yml',
        'AUTHORS',
        'CHANGELOG.md',
        'LICENSE',
        'MANIFEST.in',
        'README.md',
        'requirements.txt',
        'requirements_test.txt',
        'setup.py',
        'tox.ini',
        'pkgname/__init__.py',
        'pkgname/metadata.py',
        'pkgname/tests.py',
    )
}

REQUIRED_CONFIG_VALUES = (
    'full_name',
    'github_username',
)

OPTIONAL_CONFIG_VALUES = (
    'email',
    'twitter',
    'travis_ci',
)


class SimpleConfig(object):
    """Simple object of an ini file's section items set as attributes """

    def __init__(self, config_path, section_name):
        self._config_path = config_path
        self._section_name = section_name
        self._validate()
        self._set_config_attrs()

    def _set_config_attrs(self):
        config = self._get_config()
        for key, val in config.items():
            setattr(self, key, val)

    def _get_config(self):
        config = configparser.ConfigParser()
        config.read(self._config_path)
        return dict(config.items(self._section_name))

    def _validate(self):
        if not os.path.exists(self._config_path):
            sys.exit(u"pkgtmpl config {0} doesn't "
                     u"exist.".format(self._config_path))
        try:
            self._get_config()
        except configparser.NoSectionError:
            sys.exit(u"The section '{0}' doesn't exist "
                     u"in {1}.".format(self._section_name, self._config_path))


def validate_config_attrs(config):
    for attr in REQUIRED_CONFIG_VALUES:
        if not hasattr(config, attr):
            sys.exit(u'Config {0} is missing item '
                     u'{1}'.format(config._config_path, attr))


def validate_app_path(app_path):
    if os.path.exists(app_path):
        sys.exit(u'Path {0} already exists.'.format(app_path))


def validate_package_type_exists(package_type):
    if not os.path.isdir(get_package_type_path(package_type)):
        sys.exit(u'Package type {0} is not supported.'.format(package_type))


def get_package_type_path(package_type):
    return os.path.join(expand_path(os.path.dirname(__file__)), package_type)


def generate_files(package_type, app_path, template_context):
    env = jinja2.Environment(loader=jinja2.PackageLoader('pkgtmpl',
                                                         package_type),
                             keep_trailing_newline=True)
    os.mkdir(app_path)
    print('Created directory {0}'.format(app_path))
    for fn in FILENAMES[package_type]:

        if fn.startswith('pkgname/'):
            _, _, subdir_fn = fn.partition('/')
            pkg_path = os.path.join(app_path,
                                        template_context['package_name'])
            print('pkg_path', pkg_path)
            savepath = os.path.join(pkg_path, subdir_fn)
            if not os.path.exists(pkg_path):
                os.mkdir(pkg_path)
        else:
            savepath = os.path.join(app_path, fn)

        tmpl = env.get_template(fn)
        filecontents = tmpl.render(**template_context)
        with open(savepath, 'w') as fh:
            fh.write(filecontents)
        print('Generated file {0}'.format(os.path.join(app_path, fn)))


def git_init(app_path):
    subprocess.call(('git', 'init'), cwd=app_path)


def generate(appname, app_path, package_type, package_name=None,
             config_path=DEFAULT_CONFIG_PATH):
    app_path = expand_path(app_path)
    config = SimpleConfig(expand_path(config_path), GENERAL_CONFIG_SECTION)
    config.appname = appname
    config.package_name = package_name or appname.lower().replace('-', '_')
    validate_package_type_exists(package_type)
    validate_config_attrs(config)
    validate_app_path(app_path)
    tmpl_context = {k: v for k, v in vars(config).items()
                                 if not k.startswith('_')}
    tmpl_context['today'] = datetime.now().strftime('%Y-%m-%d')
    tmpl_context['year'] = tmpl_context['today'][0:4]

    generate_files(package_type, app_path, tmpl_context)
    git_init(app_path)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('appname', help='The name of the package')
    parser.add_argument('app_path', help='Path to create the project in')
    parser.add_argument('-p', '--package-name', help='Name of the package to '
        'create inside the app dir. Defaults to the the app name in lowercase '
        'and with dashes replaced with underscores.')
    parser.add_argument('-P', '--package-type',
                        help='The type of package to generate',
                        default='python')
    parser.add_argument('-c', '--config-path', default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()

    generate(**vars(args))


if __name__ == '__main__':
    main()
