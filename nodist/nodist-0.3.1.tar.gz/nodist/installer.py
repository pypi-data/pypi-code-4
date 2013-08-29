# coding=utf-8
# nodist is a Node.js version manager.
# Copyright (C) 2013  Kerem Çakırer

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import tarfile
import urllib
import tempfile
import shutil
import sys
from subprocess import call
from . import misc

if sys.version_info >= (3, 0):
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve

class NodeRecipe(object):
    """
    Download and install Node.js.
    Arguments:
        version: the Node.js version to be installed
        install_path: The path where Node.js is to be installed
    """
    def __init__(self, version, install_path):
        super(NodeRecipe, self).__init__()
        self.version = version
        self.install_path = install_path
        self.source_url = "http://nodejs.org/dist/v%s/node-v%s.tar.gz" % (self.version, self.version)
        self.tmpdir = tempfile.mkdtemp()

    def download(self):
        os.chdir(self.tmpdir)
        urlretrieve(self.source_url, "node-v%s.tar.gz" % self.version)
        package = tarfile.open("node-v%s.tar.gz" % self.version, 'r|gz')
        package.extractall()
        package.close()
        os.remove("node-v%s.tar.gz" % self.version)
        os.chdir("node-v%s" % self.version)

    def install(self, logging):
        if logging:
            stdout_log_path = os.path.join(misc.get_logs_path(), "stdout.log")
            stderr_log_path = os.path.join(misc.get_logs_path(), "stderr.log")
            stdout = open(stdout_log_path, 'w')
            stderr = open(stderr_log_path, 'w')
        else:
            stdout = open(os.devnull, 'w')
            stderr = stdout
        if call(["./configure", "--prefix=%s" % self.install_path],
                stdout=stdout, stderr=stderr) != 0:
            raise OSError("./configure failed")
        if call(["make"], stdout=stdout, stderr=stderr) != 0:
            raise OSError("make failed")
        if call(["make", "install"], stdout=stdout,
                stderr=stderr) != 0:
            raise OSError("make install failed")
    def cleanup(self):
        shutil.rmtree(self.tmpdir)

def create_installation(version, logging=False):
    try:
        if misc.valid_version(version):
            sys.stdout.write("Creating installation: %s.\n" % version)
            nodist_prefix = misc.get_nodist_prefix()
            installation_path = misc.get_version_path(version)
            nodejs = NodeRecipe(version, installation_path)
            sys.stdout.write("Downloading.\n")
            nodejs.download()
            sys.stdout.write("Building.\n")
            nodejs.install(logging)
            sys.stdout.write("Installed.\n")
        else:
            sys.stderr.write("Error: %s does not look like a valid version.\n" %
                    version)
    except Exception:
        err = sys.exc_info()[1]
        sys.stderr.write("Error: %s.\n" % str(err))
    finally:
        if misc.valid_version(version):
            sys.stdout.write("Cleaning up.\n")
            nodejs.cleanup()

def delete_installation(version):
    version_path = misc.get_version_path(version)
    if misc.version_exists(version):
        try:
            sys.stdout.write("Removing installation: %s.\n" % version)
            shutil.rmtree(version_path)
            os.unlink(misc.get_bin_path())
        except Exception:
            err = sys.exc_info()[1]
            sys.stderr.write("Error: %s.\n" % str(err))
