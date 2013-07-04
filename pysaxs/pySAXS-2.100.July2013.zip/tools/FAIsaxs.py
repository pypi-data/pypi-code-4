from pyFAI import geometry
from pyFAI import azimuthalIntegrator
from pySAXS.tools.isNumeric import *
import numpy
import fabio

class FAIsaxs(azimuthalIntegrator.AzimuthalIntegrator):
    
    _xmldirectory={}
    
    def importIJxml(self,filename):
        '''
        import a dictionary object from ImageJ SAXS plugins xml file
        '''
        from xml.etree import ElementTree
        element=ElementTree.parse(filename)
        root=element.getroot()
        self._xmldirectory={}
        if root.tag<>'ImageJprefs':
                raise RuntimeWarning("no ImageJ preference in this file !")
                return         
        for sube in root[0]:
            tag=sube.tag
            self._xmldirectory[tag]=sube.text
            if isNumeric(sube.text):
                    self._xmldirectory[tag]=float(sube.text)
        return 

    def setGeometry(self,filename=None):
        '''
        apply a geometry object from ImageJ SAXS dictionary
        '''
        if filename is not None:
            self.importIJxml(filename)
        #g=geometry.Geometry()
        centerX=self._xmldirectory['user.centerx']
        centerY=self._xmldirectory['user.centery']
        dd=self._xmldirectory['user.DetectorDistance']*10 #m->mm
        tilt=90.0-self._xmldirectory['user.alpha_deg']
        pixelX=self._xmldirectory['user.PixelSize']*1e4 #m->micron
        pixelY=pixelX
        wavelength=self._xmldirectory['user.wavelength']
        self.set_wavelength(wavelength*1e-9)
        self.setFit2D(dd,centerX=centerX,centerY=centerY,tilt=tilt,pixelX=pixelX,pixelY=pixelY)
        #return g
    
    
    def getIJMask(self,maskfilename=None):
        '''
        return a image from ImageJ mask defined in d (from xml)
        '''
        if maskfilename is None:
            if self._xmldirectory.has_key('user.MaskImageName'):
                maskfilename=self._xmldirectory['user.MaskImageName']
            else:
                raise RuntimeWarning("no mask defined")
        self._xmldirectory['user.MaskImageName']=maskfilename
        ma=fabio.open(maskfilename)
        mad=ma.data
        mad=mad.astype(bool)
        mad=numpy.invert(mad)
        return mad
    
    def getMaskFilename(self):
        '''
        return mask filename
        '''
        return self.getProperty('user.MaskImageName')
        
    
    def getProperty(self,property):
        if self._xmldirectory.has_key(property):
            return self._xmldirectory[property]
        else:
            return None
        