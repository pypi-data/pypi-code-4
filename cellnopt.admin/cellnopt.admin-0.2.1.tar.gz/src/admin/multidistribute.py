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
# $:Id $
"""This module is a generalisation of the :mod:`distribute` module."""
import os
import subprocess
import tempfile
from os.path import join as pj
import glob
import time
from easydev.tools import shellcmd
include = ["*"]
from distribute import DistributeRPackage


__all__ = ["MultiDistributeRPackage"]

class MultiDistributeRPackage(object):
    """Script to ease distribution of R package from SVN

        >>> d = MultiDistributeRPackage()
        >>> d.distribute()

    Best is to call multidistribute from command line::

        python multidistribute.py --revision HEAD --packages CNORdt CNORfuzzy
        python multidistribute.py --revision 666

    """

    def __init__(self, packages=[], revision="HEAD"):
        self.packages = packages
        if len(self.packages) == 0:
            self.packages = DistributeRPackage._valid_packages.keys()

        self.revision = revision
        self.packages_name_rev = []
    def distribute(self):
        """Build the distributions of all CellNOptR packages and plugins.

        List containing CellNOptR, CNORdt, CNORode, CNORfuzzy, MEIGOR, CNORfeeder


        """
        for package in self.packages:
            print("Creating %s distribution" % package)
            d = DistributeRPackage(package ,
                    revision=self.revision)
            d.logging.debugLevel="ERROR"
            d.distribute()
            self.packages_name_rev.append(d.package_name_rev)

    @staticmethod
    def help():
        """Return usage help message"""
        print("\nPURPOSE:"+__doc__)
        print("USAGE: python multidistribute.py --revision 500")
        print("USAGE: python multidistribute.py --revision 500 --packages pkg1 pkg2")
        print("--revision must be provided and given before --packages ")
        print("--packages is optional. If not provided, all packages are distributed")
        print("Possible package names are %s ." % DistributeRPackage._valid_packages.keys())


if __name__ == "__main__":
    import sys
    print("RUNNING multidistribute.py")
    print("===========================================")
    print("Author: T. Cokelaer, $Rev: 3673 $")
    import tempfile
    print(len(sys.argv))
    if "--help" in sys.argv:
        MultiDistributeRPackage.help()
    elif len(sys.argv) == 3:
        assert sys.argv[1] == "--revision", MultiDistributeRPackage.help()
        revision = sys.argv[2]
        packages = []
        d = MultiDistributeRPackage(packages, revision=revision)
        d.distribute()
    elif len(sys.argv) >= 5:
        revision = "HEAD"
        assert sys.argv[3] == "--packages", MultiDistributeRPackage.help()
        packages = sys.argv[4:]
        d = MultiDistributeRPackage(packages, revision=revision)
        d.distribute()
    else:
        print("Unrecognised format")
        MultiDistributeRPackage.help()


