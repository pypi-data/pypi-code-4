from os import linesep
import os.path
import re
from gevent import subprocess

from ci.virtualenvapi.util import split_package_name
import sys
import gevent


class VirtualEnvironment(object):
    # True if the virtual environment has been set up through open_or_create()
    _ready = False

    def __init__(self, path):
        # remove trailing slash so os.path.split() behaves correctly
        if path[-1] == '/':
            path = path[:-1]
        self.path = path

    def __str__(self):
        return self.path

    @property
    def _pip_rpath(self):
        """The relative path (from environment root) to pip."""
        return os.path.join('bin', 'pip')

    @property
    def root(self):
        """The root directory that this virtual environment exists in."""
        return os.path.split(self.path)[0]

    @property
    def name(self):
        """The name of this virtual environment (taken from its path)."""
        return os.path.basename(self.path)

    @property
    def _logfile(self):
        """Absolute path of the log file for recording installation output."""
        return os.path.join(self.path, 'build.log')

    def _create(self):
        """Executes `virtualenv` to create a new environment."""
        out = subprocess.check_output(['virtualenv', self.name], cwd=self.root)
        self._write_to_log(out, truncate=True)  # new log

    def _execute(self, args, cwd=None, env=None, return_process=False):
        """Executes the given command inside the environment and returns the output."""

        if cwd is None:
            cwd = self.path
        else:
            cwd = os.path.join(self.path, cwd)

        print
        print "-" * 40
        print cwd, ">", " ".join(args)
        print

        if not env:
            env = {}

        if not self._ready:
            self.open_or_create()
        try:
#             output = subprocess.check_output(args, cwd=self.path)

            if os.name == "nt":
                extra_path = os.path.abspath(os.path.join(self.path, "Scripts")) + ";"
            else:
                extra_path = os.path.abspath(os.path.join(self.path, "bin")) + ":"
            env["PATH"] = str(extra_path + env.get("PATH", ""))

            process = subprocess.Popen(args,
                stdout=subprocess.PIPE, cwd=cwd, env=env,
                preexec_fn=os.setsid)

            if return_process:
                return process

            while process.poll() is None:
                gevent.sleep(1)

            out, err = process.communicate()

            if out and out.strip():
                print "STDOUT:", out.strip()
            if err and err.strip():
                print "STDERR:", err.strip()

            print "~" * 10

            return out
        except OSError, e:
            # raise a more meaningful error with the program name
            prog = args[0]
            raise Exception('Error running command %s: %s' % (prog, str(e)))

    def _write_to_log(self, s, truncate=False):
        """Writes the given output to the log file, appending unless `truncate` is True."""
        # if truncate is True, set write mode to truncate
        choice = { True: 'w',
                   False: 'a'
                 }
        with open(self._logfile, choice[truncate]) as fp:
            fp.write(s + linesep)

    def _pip_exists(self):
        """Returns True if pip exists inside the virtual environment. Can be
        used as a naive way to verify that the envrionment is installed."""
        return os.path.isfile(os.path.join(self.path, self._pip_rpath))

    def open_or_create(self):
        """Attempts to open the virtual environment or creates it if it
        doesn't exist.
        XXX this should probably be expanded to do some proper checking?"""
        if not self._pip_exists():
            self._create()
        self._ready = True

    def install(self, package, force=False):
        """Installs the given package (given in pip's package syntax)
        into this virtual environment only if it is not already installed.
        If `force` is True, force an installation."""
        if not force and self.is_installed(package):
            self._write_to_log('%s is already installed, skipping (use force=True to override)' % package)
            return
        out = self._execute([self._pip_rpath, 'install', package])
        self._write_to_log(out)

    def uninstall(self, package):
        """Uninstalls the given package (given in pip's package syntax) from
        this virtual environment."""
        if not self.is_installed(package):
            self._write_to_log('%s is not installed, skipping')
            return
        out = self._execute([self._pip_rpath, 'uninstall', '-y', package])
        self._write_to_log(out)

    def is_installed(self, package):
        """Returns True if the given package (given in pip's package syntax)
        is installed in the virtual environment."""
        if package.endswith('.git'):
            pkg_name = os.path.split(package)[1][:-4]
            return pkg_name in self.installed_package_names
        pkg_tuple = split_package_name(package)
        if pkg_tuple[1] is not None:
            return pkg_tuple in self.installed_packages
        else:
            return pkg_tuple[0] in self.installed_package_names

    def upgrade(self, package):
        """Shortcut method to upgrade a package by forcing a reinstall.
        Note that this may not actually upgrade but merely reinstall if there
        is no newer version to install."""
        self.install(package, force=True)

    @property
    def installed_packages(self):
        """List of all packages that are installed in this environment."""
        pkgs = []  # : [(name, ver), ..]
        l = self._execute([self._pip_rpath, 'freeze', '-l']).split(linesep)
        for p in l:
            if p == '': continue
            pkgs.append(split_package_name(p))
        return pkgs

    @property
    def installed_package_names(self):
        """List of all package names that are installed in this environment."""
        return [name.lower() for name, _ in self.installed_packages]
