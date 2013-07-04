#!/usr/bin/env python

# This file is licensed under the CeCILL License
# See LICENSE for details.

from distutils.core import setup
from __init__ import __version__,__subversion__,__author__,__author_email__,__url__
#import pySAXS

setup(name='pySAXS',
      version=__version__+__subversion__,
      description='Python for Small Angle X-ray Scattering data acquisition',
      long_description="Python for Small Angle X-ray Scattering data acquisition, treatment and computation of model SAXS intensities",
      author=__author__,
      author_email=__author_email__,
      url=__url__,
      license='CeCILL',
      #package_dir={'LS':'LS','pySAXS' : '.'},
      package_dir={'pySAXS' : '.'},
      packages=['pySAXS','pySAXS.LS','pySAXS.guisaxs','pySAXS.guisaxs.wx','pySAXS.guisaxs.qt','pySAXS.models','pySAXS.tools','pySAXS.models.super','pySAXS.examples'],
      #all files (.dat or pdf) are specified in MANIFEST.in
      package_data = {'pySAXS' : ['doc/*','saxsdata/*','guisaxs/wx/*.gif','guisaxs/qt/*.*','*.txt','xraylib/*']},
      
    
)
