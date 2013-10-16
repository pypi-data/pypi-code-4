""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.1.1
Author  : Stefano Covino
Date    : 24/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (15/07/2010) First version.
        : (20/12/2010) Possibility of badly formatted ECS header included.
        : (23/08/2013) NUMPY_MODE in wcs.
"""

import FitsConstants
import astLib.astWCS as aw 


def GetWCS (fitsfile, extension=0, orig00=False):
    try:
        wcs = aw.WCS(fitsfile)
        wcs.NUMPY_MODE = orig00
    except IOError:
        return None,FitsConstants.FitsFileNotFound
    except ValueError:
        return None,FitsConstants.FitsWCSNotKnown
    return wcs,FitsConstants.FitsWCSFound
    


