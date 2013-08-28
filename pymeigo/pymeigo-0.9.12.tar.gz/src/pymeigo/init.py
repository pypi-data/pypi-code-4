# -*- python -*-
#
#  This file is part of pymeigo software
#
#  Copyright (c) 2011-2012 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: http://www.ebi.ac.uk/~cokelaer/pymeigo
#
##############################################################################

import rtools
from rtools import install_packages, RPackage


def install():
    pm = rtools.RPackageManager()
    if "Rsge" not in pm.installed['Package']:
        rtools.install_packages("http://cran.r-project.org/src/contrib/Archive/Rsge/Rsge_0.6.3.tar.gz")
    pm.install_packages(["snowfall", "Rsolnp"], repos=None)

    if "MEIGOR" not in pm.installed['Package']:
        pm.install_packages("http://www.cellnopt.org/downloads/MEIGOR_0.99.6_svn3222.tar.gz",
            type="source")



