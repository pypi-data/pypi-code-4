""" 

Context : SRP
Module  : SRP.REM
Version : 1.0.0
Author  : Stefano Covino
Date    : 24/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (24/08/2013) First version.
"""


import math

from SRP.SRPFits.GetHeader import GetHeader
from SRP.SRPFits.GetWCS import GetWCS
from SRP.SRPREM.GetREMSite import GetREMSite
from SRP.SRPREM.GetObj import GetObj
import SRP.SRPREM as SREM


res = {'RA' : 0.0, 'DEC' : 0.0, 'RAOff' : 0.0, 'DECOff' : 0.0, 'AZ' : 0.0, 'ALT' : 0.0, 'AZOff' : 0.0, 'ALTOff' : 0.0}


def GetREMOffsets (filename, center=None):
    head = GetHeader(filename)[0]
    wcs = GetWCS(filename)[0]
    if head == None or wcs == None:
        res['RA'] = None
        res['DEC'] = None
        res['AZ'] = None
        res['ALT'] = None
        return res
    #
    try:
        RA = head[SREM.RA]
        DEC = head[SREM.DEC]
        dobs = head[SREM.DOBS]
    except KeyError:
        res['RA'] = None
        res['DEC'] = None
        res['AZ'] = None
        res['ALT'] = None
        return res    
    #
    if center == None:
        RAc,DECc = wcs.getCentreWCSCoords()
    else:
        RAc,DECc = wcs.pix2wcs(center['x'],center['y'])
    #
    site = GetREMSite()
    site.date = dobs.replace('T',' ').replace('-','/')
    #
    nb = GetObj(RA,DEC)
    nb.compute(site)
    AZ = math.degrees(float(nb.az))
    ALT = math.degrees(float(nb.alt))
    #
    nb = GetObj(RAc,DECc)
    nb.compute(site)
    AZc = math.degrees(float(nb.az))
    ALTc = math.degrees(float(nb.alt))
    #
    res['RA'] = RA
    res['DEC'] = DEC
    res['RAOff'] = RA-RAc
    res['DECOff'] = DEC-DECc    
    res['AZ'] = AZ
    res['ALT'] = ALT
    res['AZOff'] = AZ-AZc
    res['ALTOff'] = ALT-ALTc
    #
    return res    
    