""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 06/05/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (06/05/2013) First version.
"""

import os


from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
import sqlcl


class SDSS:
    # SQL query
    sqlquery = "select p.ObjID, p.ra, p.dec, p.u, p.Err_u, p.g, p.Err_g, p.r, p.Err_r, p.i,p.Err_i, p.z, p.Err_z from photoObj p, dbo.fGetNearbyObjEq(%.6f,%.6f,%.5f) n where p.objID = n.objID AND p.type = 6"
    # SDSS entries
    class CatEntries:
        def __init__ (self,id,ra,dec,u,eu,g,eg,r,er,i,ei,z,ez):
            self.Id = id
            self.RA = float(ra)
            self.DEC = float(dec)
            inpmag = AstroMagInput (u,eu)
            self.u = inpmag.Mag
            self.eu =inpmag.eMag
            inpmag = AstroMagInput (g,eg)
            self.g = inpmag.Mag
            self.eg =inpmag.eMag
            inpmag = AstroMagInput (r,er)
            self.r = inpmag.Mag
            self.er =inpmag.eMag
            inpmag = AstroMagInput (i,ei)
            self.i = inpmag.Mag
            self.ei =inpmag.eMag
            inpmag = AstroMagInput (z,ez)
            self.z = inpmag.Mag
            self.ez =inpmag.eMag

        
        def __str__ (self):
            msg = "%30s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%9.3f\t" % (self.u, self.eu)
            msg = msg + "%10.3f\t%9.3f\t" % (self.g, self.eg)
            msg = msg + "%10.3f\t%9.3f" % (self.r, self.er)
            msg = msg + "%10.3f\t%9.3f" % (self.i, self.ei)
            msg = msg + "%10.3f\t%9.3f" % (self.z, self.ez)
            return msg
            
            
        def __cmp__ (self, other):
            if self.r < other.r:
                return -1
            elif self.r == other.r:
                return 0
            else:
                return 1
    
    
    def __init__ (self, ra, dec, radius=1.0, epoch=2000.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=epoch)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Epoch = 2000.0
        self.Radius = radius
        self.ListEntries = []
        
        
    def GetData(self):
        QueryStr = self.sqlquery % (self.RA,self.DEC,self.Radius)
        #print QueryStr
        data = sqlcl.query(QueryStr)
        datalin = data.readlines()
        if datalin != []:
            for i in range(1,len(datalin)):
                dll = datalin[i].split(',')
                id = dll[0]
                ra = dll[1]
                dec = dll[2]
                coord = AstroCoordInput(ra,dec)
                u = dll[3]
                eu = dll[4]
                g = dll[5]
                eg = dll[6]
                r = dll[7]
                er = dll[8]
                i = dll[9]
                ei = dll[10]
                z = dll[11]
                ez = dll[12]
                newinp = self.CatEntries(id,coord.RA,coord.DEC,u,eu,g,eg,r,er,i,ei,z,ez)
                # No duplicate entries
                for ii in self.ListEntries:
                    if newinp.Id == ii.Id:
                        break
                else:
                    self.ListEntries.append(newinp)
            return len(self.ListEntries)
        else:
            return None

    def __str__(self):
        msg = ''
        for i in self.ListEntries:
            msg = msg + str(i) + os.linesep
        return msg



    def Skycat(self, outname='SRP.cat'):
        msg = ''
        msg = msg + "long_name: SRP catalog for file %s\n" % (outname)
        msg = msg + "short_name: %s\n" % (outname)
        msg = msg + "url: ./%s\n" % (outname)
        msg = msg + "symbol: {} {circle blue} 4\n"
        msg = msg + "id_col: 0\n"
        msg = msg + "ra_col: 1\n"
        msg = msg + "dec_col: 2\n"
        msg = msg + "Id\tRA\tDEC\tu\teu\tg\teg\tr\ter\ti\tei\tz\tez\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
