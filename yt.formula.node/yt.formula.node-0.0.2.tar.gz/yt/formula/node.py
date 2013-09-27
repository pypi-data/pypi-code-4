"""
Installs node.js

[node]
formula = yt.formula.node
version = 0.10.16
packages =
  grunt-cli@~0.4.1
"""
from __future__ import unicode_literals
import os

from sprinter.formulabase import FormulaBase
from sprinter import lib

binary_url_template = "http://nodejs.org/dist/v{version}/node-v{version}-{os}-{architecture}.tar.gz"


class NodeFormula(FormulaBase):

    valid_options = FormulaBase.valid_options + ['packages']
    required_options = FormulaBase.required_options + ['version']

    def install(self):
        self._install_node()
        self._install_packages()
        self._link_executables()
        FormulaBase.install(self)

    def update(self):
        fresh = False
        if self.source.get('version') != self.target.get('version'):
            self.directory.remove_feature(self.feature_name)
            self._install_node()
            fresh = True
        self._install_packages(fresh=fresh)
        self._link_executables()
        FormulaBase.update(self)

    def _install_node(self):
        """ Install node.js """
        binary_url = binary_url_template.format(**self._system_info())
        self.logger.debug("Downloading and extracting node from %s..." % binary_url)
        lib.extract_targz(binary_url, self.directory.install_directory(self.feature_name),
                          remove_common_prefix=True)

    def _link_executables(self):
        """ link the executables in a directory """
        if self.source:
            self.directory.clear_feature_symlinks(self.feature_name)
        node_bin_path = os.path.join(self.directory.install_directory(self.feature_name), 'bin')
        for executable in os.listdir(node_bin_path):
            self.logger.debug("Symlinking node program %s..." % executable)
            self.directory.symlink_to_bin(executable, os.path.join(node_bin_path, executable))

    def _install_packages(self, fresh=False):
        """ Install and resolve the required npm packages """
        if not self.source or (self.source.get('packages', '') != self.target.get('packages', '')):
            remove_packages = []
            install_packages = []
            if self.source and self.source.has('packages') and not fresh:
                for package in self.source.get('packages').strip().split('\n'):
                    remove_packages.append(package.strip())
            if self.target and self.target.has('packages'):
                for package in self.target.get('packages').strip().split('\n'):
                    package = package.strip()
                    if package in remove_packages:
                        remove_packages.remove(package)
                    install_packages.append(package)
            for package in remove_packages:
                lib.call("bin/npm uninstall --verbose %s" % package,
                         cwd=self.directory.install_directory(self.feature_name))
            for package in install_packages:
                lib.call("bin/npm install --verbose -sg %s" % package,
                         cwd=self.directory.install_directory(self.feature_name))
                
    def _system_info(self):
        """ return info about the system """
        manifest = self.target or self.source
        return {
            'version': manifest.get('version'),
            'os': 'darwin' if self.system.isOSX() else 'linux',
            'architecture': 'x64' if self.system.is64bit() else 'x86'
        }

    def validate(self):
        FormulaBase.validate(self)
        if self.target:
            versions = self.target.get('version').split('.')
            if len(versions) != 3:
                self._log_error("Version string %s is invalid! please format it as : X.X.X")
            for v in versions:
                try:
                    int(v)
                except ValueError:
                    self._log_error("Versions must all be integers! %s is not one" % v)
