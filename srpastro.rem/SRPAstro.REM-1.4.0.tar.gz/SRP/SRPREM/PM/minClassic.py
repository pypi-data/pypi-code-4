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

History : (23/08/2012) First version.
        : (22/08/2013) Improvement.
"""


from Classic import Classic
from SRP.SRPMath.FastAngularDistance import FastAngularDistance



def minClassic ((c_AN,c_AE,c_NPAE,c_BNP,c_TF,c_AOFS,c_EOFS),taz,talt,oaz,oalt):
    caz, calt = Classic((taz,talt),(c_AN,c_AE,c_NPAE,c_BNP,c_TF,c_AOFS,c_EOFS))
    return FastAngularDistance(oaz,oalt,caz,calt).sum()

