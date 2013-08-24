""" 

Context : SRP
Module  : REM
Version : 1.0.24
Author  : Stefano Covino
Date    : 24/08/2013
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
        : (14/08/2013) V. 1.3.3b1. V. 1.3.3b2.
        : (15/08/2013) V. 1.3.3b3.
        : (17/08/2013) V. 1.3.3b4.
        : (21/08/2013) V. 1.4.0b1., 1.4.0b2.
        : (22/08/2013) V. 1.4.0b3.
        : (23/08/2013) V. 1.4.0b4.
        : (23/08/2013) V. 1.4.0.
"""

__version__ = '1.4.0'



__all__ =  ['GetObj', 'GetREMOffsets', 'GetREMSite']



# REM pixel size
REMIRPixSize    = 1.22
ROSSPixSize     = 0.59
ROS2PixSize     = 0.59


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

# REM headers
RA          =   'RA'
DEC         =   'DEC'
DOBS        =   'DATE-OBS'


