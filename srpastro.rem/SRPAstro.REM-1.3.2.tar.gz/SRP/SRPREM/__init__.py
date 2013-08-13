""" 

Context : SRP
Module  : REM
Version : 1.0.15
Author  : Stefano Covino
Date    : 13/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (16/12/2011) First version.
        : (12/01/2012) V. 1.1.0b1.
        : (06/02/2012) V. 1.1.0.
        : (01/04/2012) V. 1.1.1b1.
        : (04/04/2012) V. 1.2.0b1 and new constant.
        : (18/04/2012) V. 1.2.0.
        : (01/08/2012) V. 1.2.1b1.
        : (22/08/2012) V. 1.3.0b1.
        : (29/08/2012) V. 1.3.0.
        : (31/08/2012) V. 1.3.1b1.
        : (22/03/2013) V. 1.3.1.
        : (22/04/2013) New ROS2 pixel size. and V. 1.3.2b1
        : (21/06/2013) New camera code.
        : (01/07/2013) Parameter name check in REM pointing model.
        : (13/08/2013) Better minimization in pointing model computation. V. 1.3.2.
"""

__version__ = '1.3.2'



__all__ =  ['GetObj', 'GetREMSite']



# REM pixel size
REMIRPixSize    = 1.22
ROSSPixSize     = 0.59


# Constants
REMIR   =   'REMIR'
ROSS    =   'REM-ROSS'
ROS2    =   'REM-ROS2'
CAMERA  =   'INSTRUME'

# External commands
astro   =   'SRPAstrometry'

# Observatory location
REMLAT = '-29.2567'
REMLONG = '-70.7292'
REMHEIGHT = 2347.0



