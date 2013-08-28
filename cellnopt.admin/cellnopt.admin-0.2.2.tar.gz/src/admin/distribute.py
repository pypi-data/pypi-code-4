# -*- python -*-
#
#  This file is part of the cellnopt software
#
#  Copyright (c) 2011-2012 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  https://pypi.python.org/pypi/cellnopt.admin
#  http://pythonhosted.org/cellnopt.admin
#
##############################################################################
# $Id: distribute.py 3673 2013-06-05 09:43:14Z cokelaer $
"""This module provides tools to check out a revision of a SVN directory
into a temporary directory and to create a tar ball out of that
SVN copy and copy the final tar ball in the directory where this script is
called. Sub directories such as .svn are removed. The temporary directory is
also removed.

This is coded in the :class:`DistributeRPackage`  class. This module is also executable
provided with cellnopt.admin package called cellnopt_distribute.


"""
import os
import subprocess
import tempfile
from os.path import join as pj
import glob
import time
import sys

from easydev.tools import shellcmd
from easydev import Logging
include = ["*"]


__all__ = ["DistributeRPackage"]

class DistributeRPackage(object):
    """Class to ease distribution of CellNOptR packages from SVN


    Can be used for any SVN containing valid R packages by setting the
    repository URL

        >>> d = DistributeRPackage("CNORdt")
        >>> d.distribute()

    You can also use the executable provided in cellnopt.admin package itself::

        cellnopt_distribute --package CNORdt --revision HEAD

    equivalent to (if you have the sources)::

        python distribute.py --package CNORdt --revision 666

    

    """
    #: mapping between package name and actual directory name 
    _valid_packages = {"CellNOptR":"CellNOptR",
                       "CNORdt":pj("CNOR_dt","CNORdt"),
                       "CNORode":pj("CNOR_ode","CNORode"),
                       "CNORfuzzy":"CNOR_fuzzy",
                       "CNORfeeder":"CNOR_add_links",
                       "MEIGOR": pj('essR','MEIGOR')}

    def __init__(self, package, url=None, revision="HEAD", build_options="--no-vignettes"):
        """

        :param str package: name of a valid package (e.g., CellNOptR)
        :param str url:
        :param revision: SVN revision (default is HEAD )
        :param build_options: additional build options for R (default is --no-vignettes)

        You can also change the logging level (e.g., self.logging.debugLevel="WARNING")

        """
        if url == None:
            self.url = "https://svn.ebi.ac.uk/sysbiomed/trunk"
        else:
            self.url = url
        self.revision_user = revision
        self.exclude = [".svn"]
        self.package = package
        self.dtemp = None
        self.cwd = os.getcwd()
        self.build_options = build_options
        self.logging = Logging("INFO")

    def _get_version(self):
        data = open(self.dtemp + os.sep + self.package + os.sep + "DESCRIPTION", "r").read()
        res = [x.split(':')[1].strip() for x in data.split("\n") if x.startswith('Version')]
        return res[0]
    # no need to make it public
    #version = property(_get_version, doc="return version of the R package")

    def _get_package_directory(self):
        return DistributeRPackage._valid_packages[self.package]

    def _create_temp_directory(self):
        self.dtemp = tempfile.mkdtemp()

    def _checkout_svn(self):
        self.logging.info("1. Gettting the source from SVN --------------")
        if self.dtemp == None:
            self._create_temp_directory()
        target = pj(self.dtemp, self.package)
        path = self.url + '/' + self._get_package_directory()
        cmd = "svn co -r%s %s/%s %s" % (self.revision_user, self.url,
            DistributeRPackage._valid_packages[self.package], pj(self.dtemp, self.package))
        self.logging.info(cmd,)
        try:
            ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            ret.wait()
            if ret.poll()!=0:
                raise Exception
            self.logging.info('...done')
        except Exception:
            raise Exception

    @staticmethod
    def help():
        """Return usage help message"""
        print("\nPURPOSE:"+__doc__)
        print("USAGE: python distribute.py --package valid_package_name")
        print("USAGE: python distribute.py --package valid_package_name --revision 500")
        print("USAGE: python distribute.py --svn valid_SVN --package valid_package_name --revision 500")
        print("")
        print("Possible package names are %s ." % DistributeRPackage._valid_packages.keys())
        #sys.exit(1)

    def distribute(self):
        """This is the main method to create package distribution.

        It follows these steps:

         #. creates temp directoy
         #. svn checkout clean revision
         #. calls R CMD build

        """
        if self.dtemp == None:
            self._create_temp_directory()
        try:
            self._checkout_svn()
        except Exception, e:
            self._stop()
            raise Exception(e)

        self._build_R_package()
        self._stop()

    def _stop(self):
        import shutil
        if self.dtemp:
            shutil.rmtree(self.dtemp)

    def _get_revision(self):
        self.logging.info("Getting revision")
        try:

            tag="Last Changed Rev"
            cmdsvn = """svn info %s | grep "%s" | awk '{print $4}' """ % (pj(self.dtemp, self.package), tag)
            #tag="Revision"
            #cmdsvn = """svn info %s | grep "%s" | awk '{print $2}' """ % (pj(self.dtemp, self.package), tag)
            self.logging.info( cmdsvn)
            ret = subprocess.Popen(cmdsvn, stdout=subprocess.PIPE, shell=True)
            ret.wait()
            revision = ret.stdout.read().strip()
        except Exception, e:
            revision = self.revision_user
            raise Exception(e)
        self.logging.info("This is revision %s. Making a tar ball." % revision)
        return revision
    # no need to make it public
    #revision = property(_get_revision, doc="return SVN revision")

    def _build_R_package(self):
        # first, build the R package
        self.logging.info("2. Creating the package distribution ----------------------"),
        t0 = time.time()
        cmdR = "R CMD build %s %s" % (self.dtemp+os.sep+self.package, self.build_options)
        shellcmd(cmdR, verbose=True)

        import glob
        package_name = self.package + "_" + self._get_version() + ".tar.gz"
        #rename the package name
        package_name_rev = self.package + "_"+self._get_version() + "_svn" + self._get_revision() + ".tar.gz"
        self.logging.info("3. "),
        #shellcmd("ls %s" % (self.dtemp), verbose=True)
        #shellcmd("ls", verbose=True)
        shellcmd("mv %s %s" % (package_name, package_name_rev), verbose=True)

        t1 = time.time()
        self.logging.info("Distribution built in " + str(t1-t0) + " seconds.")
        self.logging.info("File %s available in the current directory " % package_name_rev)
        self.package_name_rev = package_name_rev



def main():
    """Main executable related to distribute

    type::

        python distribute.py --help

    or::

        cellnopt_distribute --help

    """
    import sys
    print("RUNNING distribute.py")
    print("===========================================")
    print("Author: T. Cokelaer, $Rev: 3673 $")
    if len(sys.argv)!=3 and len(sys.argv)!=5:
        DistributeRPackage.help()
    else:
        import tempfile
        assert sys.argv[1] == "--package", DistributeRPackage.help()
        package = sys.argv[2]
        if len(sys.argv) == 5:
            assert sys.argv[3] == "--revision", DistributeRPackage.help()
            revision = sys.argv[4]
        else:
            revision = "HEAD"
        d = DistributeRPackage(package, revision=revision)
        d.distribute()

if __name__ == "__main__":
    main()
