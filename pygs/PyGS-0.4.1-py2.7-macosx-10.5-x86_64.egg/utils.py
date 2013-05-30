'''
Created on Dec 3, 2012

@author: Steven
'''

import numpy as np

def FD_bins(data):
        """
        Calculates the optimal number of bins for a histogram based on Freedman-Diaconis equation
        """
        from scipy.stats import scoreatpercentile as sap
        
        
        #Use the Freedman-Diaconis method to calculate the bin number
        IQR = sap(data,75) - sap(data,25)
        width = 2*IQR/len(data)**(1./3.)
        bins = np.ceil((max(data)-min(data))/width)
        
        return bins
    
def sph2car(r,theta,phi):
    """
    Takes a spherical polar co-ordinate vector and returns a cartesian one
    """
    x = r*np.cos(theta)*np.sin(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(phi)
        
    return x,y,z
    
def car2sph(x,y,z):
    """
    Takes a cartesian vector and returns a spherical polar one
    """
        
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arctan2(y,x)
    phi = np.arccos(z/r)
        
    return r,theta,phi