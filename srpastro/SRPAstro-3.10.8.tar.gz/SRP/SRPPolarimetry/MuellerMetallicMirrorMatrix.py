""" Utility functions and classes for SRP

Context : SRP
Module  : Polarimetry
Version : 1.0.0
Author  : Stefano Covino
Date    : 04/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : angle is in radians, real and imaginary part of the refraction index
            can be found at: http://refractiveindex.info/
            From Joos et al., SPIE, 7016
            

History : (04/02/2012) First version.

"""

import math
import numpy


def MuellerMetallicMirrorMatrix (refrindex=1.26, extcoeff=7.19, angle=math.radians(45.0)):
    p = refrindex**2-extcoeff**2-math.sin(angle)**2
    q = 2*refrindex*extcoeff
    #
    rpiu = (1./math.sqrt(2.))*math.sqrt(p+math.sqrt(p**2+q**2))
    rmeno = (1./math.sqrt(2.))*math.sqrt(-p+math.sqrt(p**2+q**2))
    s = math.sin(angle)*math.tan(angle)
    #
    rho = math.sqrt((math.sqrt(p**2+q**2)+s**2-2*s*rpiu)/
            (math.sqrt(p**2+q**2)+s**2+2*s*rpiu))
    delta = math.atan2(2*s*rmeno,math.sqrt(p**2+q**2)+s**2+2*s*rpiu)
    #
    r1 = [1.+rho**2, 1-rho**2, 0., 0.]
    r2 = [1.-rho**2, 1.+rho**2, 0., 0.]
    r3 = [0., 0., -2.*rho*math.cos(delta), -2.*rho*math.sin(delta)]
    r4 = [0., 0., 2.*rho*math.sin(delta), -2.*rho*math.cos(delta)]
    return 0.5*numpy.matrix([r1, r2, r3, r4])
