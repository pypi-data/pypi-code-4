""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.1.0
Author  : Stefano Covino
Date    : 22/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (22/08/2012) First version.
        : (01/07/2013) Check of parameter names.
        : (22/08/2013) Just offsets.
"""

import numpy


def Full ((az,alt),(f_AAN,f_EAE,f_NPAE,f_BNP,f_AES,f_AEC,f_EES,f_EEC,f_AOFS,f_EOFS)):
    # AAN: error in the leveling of the telescope toward north
    # EAE: error in the leveling of the telescope toward east
    # NPAE: non-perpendicularity of the azimuth and elevation axis
    # BNP: non-perpendicularity of the optical and the elevation axis
    # AES, AEC, EES, EEC:  eccentricity of the encoders
    # AOFS: azimuth zero point correction
    # EOFS: altitude zero point correction
    naz = f_AAN * numpy.sin(numpy.radians(az)) * numpy.tan(numpy.radians(alt)) - f_EAE * numpy.cos(numpy.radians(az)) * numpy.tan(numpy.radians(alt)) + f_NPAE * numpy.tan(numpy.radians(alt))  - f_BNP / numpy.cos(numpy.radians(alt)) + f_AOFS + f_AES * numpy.sin(numpy.radians(az)) + f_AEC * numpy.cos(numpy.radians(az))
    nalt = f_AAN * numpy.cos(numpy.radians(az)) + f_EAE * numpy.sin(numpy.radians(az)) + f_EOFS + f_EES * numpy.sin(numpy.radians(alt)) + f_EEC * numpy.cos(numpy.radians(alt))
    return naz, nalt

