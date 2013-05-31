'''
Created on Dec 3, 2012

@author: Steven

Throughout this module "min" when applied to magnitudes means the numerical
minimum, ie. BRIGHTEST. And conversely "max" corresponds to DIM objects.
'''
##################################################################
# IMPORTS
##################################################################
import sys

try:
    import numpy as np
except:
    sys.exit("Please install Numpy")

try:
    import matplotlib.pyplot as plt
except:
    sys.exit("Please install Matplotlib")

try:
    from fort.luminosity import lumfunc_denom#luminosity
    fort_routines = True
except:
    print "Warning: fortran luminosity routines not found. "
    fort_routines = False
try:
    import pandas
except:
    print "Please install pandas!"

def k_correct(redshifts,gr_colour):
    """
    Calculates the K-correction using the method of Chilingarian et al. (2010); see arxiv.org/pdf/1002.2360v1.pdf
    Values of coeff are from online table (but might be a little more rigorous to use values from their Table A3).
    This method has only been empirically verified using actual spectral data for redshifts < 0.28.
    Also, their method excluded z < 0.03, in order to minimize aperture effects.
    For these reasons, 0.03 < z < 0.28.
    """
    #Coefficients from the online table.
    coeff = np.array([[0, 0, 0, 0],
                      [-1.61166, 3.87173, -3.87312, 2.66605],
                      [8.48781, 13.2126, -6.4946, -7.31552],
                      [-87.2971, -35.0474, 41.5335, 0],
                      [271.64, -26.9081, 0, 0],
                      [-232.289, 0, 0, 0]])

    #Coefficients from the table A3
    coeff_A3 = np.array([[0, 0, 0, 0],
                         [-1.61294, 3.81378, -3.56114, 2.47133],
                         [9.13285, 9.85141, -5.1432, -7.02213],
                         [-81.8341, -30.3631, 38.5052, 0],
                         [250.732, -25.0159, 0, 0],
                         [-215.377, 0, 0, 0]])

    kcor = np.zeros_like(redshifts)
    for x, a in enumerate(coeff):
        for y, b in enumerate(coeff[x]):
            kcor += coeff_A3[x][y] * redshifts ** x * gr_colour ** y

    return kcor


def lum_dist(redshift, c_dist):
    """
    Calculates the luminosity distance d_L according to d_L = (1+z)*c_dist
    where z is the redshift and c_dist is the line-of-sight comoving distance.
    Note that, in general, d_L = (1+z)*D_M, where D_M is the transverse comoving distance.
    For a "flat" cosmology (such as we are assuming here), D_M = c_dist
    """

    lum_dist = c_dist * (1 + redshift)
    return lum_dist

def absolute_mag(mag_r, lum_dist, kcor=None):
    """
    Calculates the absolute magnitude from
    M = m - 5*log(lum_dist) -25 -K(z),
    where . . .
    m is the apparent magnitude
    log is the base-10 logarithm
    lum_dist is the luminosity distance (in Mpc),
    and K(z) is the K-correction.
    See also http://www.maths.qmul.ac.uk/~wjs/MTH726U/appendix1.pdf:  we may need to subtract another term from the RHS
    of the equation below, an extinction term due to intervening material, lambda_F
    ***Important!!! Need to convert Fibermags to conventional "Pogson" magnitudes before getting absolute magnitudes:
    See http://www.sdss.org/dr5/algorithms/fluxcal.html
    """
    if kcor is not None:
        absmag = mag_r - 5 * np.log10(lum_dist) - 25 - kcor
    else:
        absmag = mag_r - 5 * np.log10(lum_dist) - 25

    return absmag

def absmag_to_lum(absmag):
    """
    Calculates the luminosity (actually, the base 10 log of the luminosity) using apparent magnitudes
    
    Note that the absolute magnitude of the sun is 4.83.
    WARNING:  Need to make sure that we are using abs. mag. for sun in r-band!
    """

    lum = np.log10(3.839 * 10 ** 26) + ((4.83 - absmag) / 2.512)

    return lum

def mag_bounds_optimal(absmag,Np,min_acceptable=0,verbose=True):
    """
    Calculates optimal bounds on absolute magnitude for binning (all bins have
    more than min_acceptable galaxies)
    """
    
    excluded = len(absmag)
    for minm in np.arange(-25,-20,0.5):
        for maxm in np.arange(-15,-10,0.5):
            bins = np.linspace(minm,maxm,Np+1)
            hist, bins = np.histogram(absmag,bins=bins)
     #       hist2,bins = np.histogram(absmagmax,bins=bins)                
            if np.min(hist) > min_acceptable:# and np.min(hist2)>min_acceptable:
                #The histogram is ok, count number of galaxies excluded
                mag_excluded = np.logical_or(absmag<minm,absmag>maxm)
                #magmax_excluded = absmagmax > maxm                     
                excluded_new = np.sum(mag_excluded )
                if excluded_new < excluded:
                    final_min_m = minm
                    final_max_m = maxm
                    excluded = excluded_new
                
    if excluded == len(absmag):
        sys.exit("No bounds found acceptable, try again with fewer bins")
    if verbose:
        print "Optimal acceptable bin structure with ", Np," bins has"
        print "M_min = ", final_min_m
        print "M_max = ", final_max_m
        print "And leaves out ", excluded, " galaxies"
      
    return final_min_m, final_max_m
                

def lum_func(absmag,mag_r,c_dist,k_corr,Np,min_acceptable=0,eps=0.01,verbose=True):
    """
    Calculates the luminosity function of galaxies in Np bins.
    Uses EEP method only currently (that may be expanded)
    """
    if not fort_routines:
        print "Sorry the fortran routines for calculating this function are not available"
        return
        
    #Set up the bin structure
    M_min, M_max = mag_bounds_optimal(absmag,Np,min_acceptable,verbose=verbose)
    bin_edges,deltaM = np.linspace(M_min,M_max,Np+1,retstep=True)
    bin_centres = bin_edges[:-1] + deltaM/2

    #Mask relevant arrays to lie between M_min and M_max
    mask = np.logical_and(absmag>M_min,absmag<M_max)
    
    absmag = absmag[mask]
    mag_r = mag_r[mask]
    c_dist = c_dist[mask]
    k_corr = k_corr[mask]
    
    #Get absmagmax
    max_absmag = absmagmax(np.max(mag_r),c_dist,k_corr)

    nanmask = np.logical_not(np.isnan(max_absmag))
    
    absmag = absmag[mask]
    mag_r = mag_r[mask]
    c_dist = c_dist[mask]
    k_corr = k_corr[mask]
    max_absmag = max_absmag[nanmask]

    #Make the array phi which will hold all iterations of the lum func.
    phi = pandas.DataFrame(index = bin_centres)         

    # Get initial trial phi
    phi[0] = np.histogram(absmag,bins = bin_edges)[0]/deltaM #divide by deltaM because of bin-wdth normalization
    assert np.min(np.array(phi[0]))>min_acceptable
    
    #Now do the iterations etc.
#    difference = 10.0
    l = 0
    while l<4:#difference > eps:
        l += 1
        denom = lumfunc_denom.denom(np = Np,
                                      ngal = len(absmag),
                                      bins = np.asfortranarray(bin_edges),
                                      phi = np.asfortranarray(phi[l-1]),
                                      deltam = deltaM,
                                      absmagmax = np.asfortranarray(max_absmag)
                                      )
        phi[l] = phi[0]/denom #No need to divide by deltaM as phi[0] is W/deltaM
        
        #difference = np.sum(np.abs(phi[l]-phi[l-1]))
        
    iterations = l

    #A quick and dirty plot    
    phi.plot()
    plt.show()
    return phi, iterations
            
##    def _H(self,absmagmax,bin_centre,deltaM):
#        """
#        The function H() from eq. 1.23 of Jake's MLE explanation
#        """
#
#        diff = absmagmax - bin_centre
#        if diff <= -deltaM/2:
#            return 0
#        elif diff > deltaM/2:
#            return 1
#        else:
#            return diff/deltaM + 0.5
#            
#    def _denom_of_denom(self,absmagmax,bins,Np,phi):
#        """
#        Calculates denom of denom of eq.1.28
#        """
#        
#        the_bin = (absmagmax - bins[0])%(bins[1]-bins[0])
#        H = np.zeros(Np)
#        H[:the_bin] = 0
#        H[the_bin] = (absmagmax - bins[the_bin])/(bins[1]-bins[0]) + 0.5
#        H[the_bin+1:] = 1
#        
#        H = phi*H*(bins[1]-bins[0])
#        
#        return np.sum(H)
#        
#    def _denom(self,bins,Np,phi,bin_centre,deltaM,absmagmax):
#        """
#        Calculates denom (as a whole) of eq.1.28
#        """
#
#        denom = 0
#        for i,mag in enumerate(absmagmax):
#            top = self._H(mag,bin_centre,deltaM)            
#            bottom= self._denom_of_denom(mag,bins,Np,phi)
#            denom += top/bottom
#            
#        return denom
        
def absmagmax(self,maxmagr,dist,kcorr):
    """
    The DIMMEST an object can be at a given redshift/distance
    """
    return maxmagr -5.0*np.log10(self._LumDistance(dist))-25.0-kcorr
    
def absmagmin(self,minmagr,dist,kcorr):
    """
    The BRIGHTEST an object can be at a given redshift/distance
    """
    
    return minmagr -5.0*np.log10(self._LumDistance(dist))-25.0-kcorr
        
        
        
