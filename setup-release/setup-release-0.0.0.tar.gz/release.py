#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import xmlrpclib

# Third-Party Libairies
import setuptools
import sh


class Release(setuptools.Command):

    description = "Manage software releases"

    user_options = [
      ("list", "l", "list package version info"),
    ]

    def initialize_options(self):
        self.list = None

    def finalize_options(self):
        pass

    def run(self):
        if self.list:
            self.display_package_info()
        else:
            self.release_on_pypi()

    def display_package_info(self):
        self.name = self.distribution.get_name()
        self.version = self.distribution.get_version()
        pypi = xmlrpclib.ServerProxy("http://pypi.python.org/pypi")
        print "current version: {0}".format(self.version)
        releases = pypi.package_releases(self.name) # show visible only
        print "Pypi releases: {0}".format(", ".join(releases))

    def check(self):
        self.display_package_info()
        answer = raw_input("Accept ? [Y/n] ")
        answer = answer or "Y"
        return (answer[0].upper() == "Y")        

    def release_on_pypi(self):
        if self.check():
            setup = sh.Command("./setup.py")

            # needs to be non-interactive: use a .pypirc file
            response = setup("register")
            print response
            last_line = str(response).splitlines()[-1]
            if not "(200)" in last_line:
                raise RuntimeError(last_line)


            response = setup("sdist", "upload")
            print response
            last_line = str(response).splitlines()[-1]
            if not "(200)" in last_line:
                raise RuntimeError(last_line)


