"""
This module will handle Node installations.
Note that this module should not print anything
and instead raise exceptions.
The install module will handle these.
"""

import os
import sys
import tarfile
import shutil
from subprocess import call

import nodevers.shared as shared

if sys.version_info >= (3, 0):
    from urllib.error import URLError
    from urllib.error import HTTPError
    from urllib.error import ContentTooShortError
    from urllib.request import urlopen
    from urllib.request import urlretrieve
else:
    from urllib2 import URLError
    from urllib2 import HTTPError
    from urllib import ContentTooShortError
    from urllib2 import urlopen
    from urllib import urlretrieve



class BuildError(StandardError):
    """
    Will be thrown when ./configure, make
    or make install fails.
    """
    pass


class NodeInstaller(object):
    """
    This will install Node.
    """
    def __init__(self, ver, install_path, build_args):
        self.ver = ver
        self.install_path = install_path
        self.build_args = build_args
        self.url = "http://nodejs.org/dist/v%s/node-v%s.tar.gz" % (self.ver,
                self.ver)
        try:
            urlopen(self.url)
        except HTTPError:
            raise shared.NoSuchVersionError("cannot download node-v%s.tar.gz" % self.ver)
        except URLError:
            raise IOError("make sure you are connected to the Internet")
        self.tmpdir = shared.get_tmp_dir()
        try:
            logfile_path = os.path.join(os.path.join(shared.get_nodevers_prefix(), "log"))
            self.logfile = open(logfile_path, "w")
        except IOError:
            self.logfile = open(os.devnull, 'w')

    def download_source(self):
        """
        This will download the source packages.
        """
        os.chdir(self.tmpdir)
        self.package = "node-v%s.tar.gz" % self.ver
        if os.path.exists(self.package):
            pass
        else:
            try:
                urlretrieve(self.url, self.package)
            except IOError:
                raise IOError("make sure you are connected to the Internet")
            except ContentTooShortError:
                raise IOError("the download was interrupted")
    def extract_source(self):
        """
        This method will extract the source files from
        download package.
        In case it fails, it will remove the package.
        """
        try:
            extract = tarfile.open(self.package, "r|gz")
        except tarfile.ReadError:
            os.remove(self.package)
            raise IOError("%s is corrupted" % self.package)
        extract.extractall()
        extract.close()
        os.chdir("node-v%s" % self.ver)

    def patch(self):
        """
        Try to apply patches returned by shared.get_patches_list.
        """
        patches_list = shared.get_patches_list(self.ver)
        for patch_path in patches_list:
            patch = open(patch_path, 'r')
            try:
                exit_code = call(["patch"], stdout=self.logfile,
                        stderr=self.logfile, stdin=patch)
                if exit_code is not 0:
                    raise BuildError("patching has failed")
            except OSError:
                raise shared.MissingToolError("patch is missing")
            finally:
                patch.close()

    def configure(self):
        """
        Configure Node.
        """
        exit_code = call([shared.python(), "configure",
            "--prefix=%s" % self.install_path,
            "%s" % self.build_args],
            stdout=self.logfile, stderr=self.logfile)
        if exit_code is not 0:
            raise BuildError("configure has failed")
    def make(self):
        """
        Build Node.
        """
        exit_code = call([shared.gmake()], stdout=self.logfile,
                stderr=self.logfile)
        if exit_code is not 0:
            raise BuildError("make has failed")

    def make_install(self):
        """
        Install Node.
        """
        exit_code = call([shared.gmake(), "install"],
                stdout=self.logfile, stderr=self.logfile)
        if exit_code is not 0:
            raise BuildError("make install has failed")

    def cleanup(self):
        """
        Remove the build tree &
        close the log file.
        """
        clean_path = os.path.join(self.tmpdir, "node-v%s" % self.ver)
        shutil.rmtree(clean_path)
        self.logfile.close()
