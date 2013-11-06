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
    from fort.luminosity import lumfunc_denom  #luminosity
    fort_routines = True
except:
    print "Warning: fortran luminosity routines not found. "
    fort_routines = False
try:
    import pandas
except:
    print "Please install pandas!"

def k_correct(redshifts, gr_colour):
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

def absolute_mag(mag_r, lum_dist, kcor=0, extinction=0):
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

    return mag_r - 5 * np.log10(lum_dist) - 25 - kcor - extinction

def absmag_to_lum(absmag):
    """
    Calculates the luminosity (actually, the base 10 log of the luminosity) using apparent magnitudes
    
    Note that the absolute magnitude of the sun is 4.83.
    WARNING:  Need to make sure that we are using abs. mag. for sun in r-band!
    """

    lum = np.log10(3.839 * 10 ** 26) + ((4.83 - absmag) / 2.512)

    return lum

def mag_bounds_optimal(absmag, Np, min_acceptable=1, verbose=True):
    """
    Calculates optimal bounds on absolute magnitude for binning (all bins have
    more than min_acceptable galaxies)
    """

    excluded = len(absmag)
    for minm in np.linspace(-25, -22, 7):
        for maxm in np.linspace(-17, -15, 5):
            deltam = (maxm - minm) / (Np - 1)
            #The bins go from minm-deltam/2 to maxm+deltam/2 (ie. treat minm and maxm as CENTRES of bins).
            bins = np.linspace((minm - deltam / 2), (maxm + deltam / 2), Np + 1)
            hist, bins = np.histogram(absmag, bins=bins)
            if np.min(hist) >= min_acceptable:
                #The histogram is ok, count number of galaxies excluded
                mag_excluded = np.logical_or(absmag < minm - deltam / 2, absmag > maxm + deltam / 2)
                excluded_new = np.sum(mag_excluded)
                if excluded_new < excluded:
                    final_min_m = minm
                    final_max_m = maxm
                    excluded = excluded_new

    if excluded == len(absmag):
        raise ValueError("No bounds found acceptable, try again with fewer bins")
    if verbose:
        print "Optimal acceptable bin structure with ", Np, " bins has"
        print "M_min = ", final_min_m
        print "M_max = ", final_max_m
        print "And leaves out ", excluded, " galaxies"

    return final_min_m, final_max_m


def EEP(absmag, apmag, Np, min_acceptable=1, eps=0.01, max_iter=10,
             verbose=True):
    """
    Calculates the luminosity function of galaxies in Np bins using SWML of EEP.
    
    INPUT PARAMETERS
    absmag             -- a vector of absolute magnitudes (AB)
    apmag              -- a vector of apparent magnitudes, same length as absmag
    Np                 -- the number of bins in which to output the luminosity function
    min_acceptable [1] -- the minimum number of galaxies needed in each bin for a valid result
    eps [0.01]         -- the target convergence parameter. The mean fractional change between iterations.
    max_iter [10]      -- the maximum number of iterations to attempt reaching convergence
    verbose [True]     -- whether to print out extra information
    
    OUTPUT
    phi        -- a pandas.DataFrame object containing all iterations of the luminosity function,
                    indexed by the bin centre, and labelled by the iteration number
    iterations -- the number of iterations used.
    """
    if not fort_routines:
        raise ValueError("Sorry the fortran routines for calculating this function are not available")

    #Set up the bin structure
    M_min, M_max = mag_bounds_optimal(absmag, Np, min_acceptable, verbose=verbose)
    bin_centres, deltaM = np.linspace(M_min, M_max, Np , retstep=True)
    bin_edges = np.hstack((bin_centres - deltaM / 2, bin_centres[-1] + deltaM / 2))

    #Mask relevant arrays to lie between M_min and M_max
    mask = np.logical_and(absmag >= M_min - deltaM / 2, absmag <= M_max + deltaM / 2)

    absmag = np.array(absmag[mask])
    apmag = np.array(apmag[mask])

    #Get absmagmax (dimmest a galaxy can be at given redshift).
    max_absmag = absmagmax(np.max(apmag), apmag, absmag)


#    nanmask = np.logical_not(np.isnan(max_absmag))
#
#    absmag = absmag[nanmask]
#    mag_r = mag_r[nanmask]
#    c_dist = c_dist[nanmask]
#    k_corr = k_corr[nanmask]
#    max_absmag = max_absmag[nanmask]

    #Make the array phi which will hold all iterations of the lum func.
    phi = pandas.DataFrame(index=bin_centres)

    # Get initial trial phi THIS IS ALSO THE VALUE OF W(k)
    phi[0] = np.histogram(absmag, bins=bin_edges)[0] / deltaM  #divide by deltaM because of bin-width normalization

    #Also get the matrix H(ngal,Np)
    Hmat = lumfunc_denom.get_hmatrix(np=Np,
                                     ngal=len(absmag),
                                     absmagmax=np.asfortranarray(max_absmag),
                                     bins=np.asfortranarray(bin_edges),
                                     deltam=deltaM)

    #Now do the iterations etc.
    difference = 10.0
    l = 0
    while l < max_iter and difference > eps:  #difference > eps:
        l += 1
        denom = lumfunc_denom.denom(np=Np,
                                      ngal=len(absmag),
                                      phi=np.asfortranarray(phi[l - 1]),
                                      deltam=deltaM,
                                      hmat=np.asfortranarray(Hmat)
                                      )
        print "Iteration ", l

        phi[l] = phi[0] / denom  #No need to divide by deltaM as phi[0] is W/deltaM
        difference = np.mean(np.abs((phi[l] - phi[l - 1]) / phi[l]))

    iterations = l
    if iterations == max_iter and difference > eps:
        print "WARNING: METHOD DID NOT CONVERGE, MEAN DIFFERENCE STILL: ", difference

    return phi, iterations

#def c_method(appmag, absmag, z):
#    """
#    This is basically a copy off the web for checking
#    """
#    m_max = np.max(appmag)
#
#    zbins, dist_z, err_z, Mbins, dist_M, err_M = get_lf_cmethod(z, appmag, absmag, m_max)
#
#def get_lf_cmethod(z, appmag, absmag, m_max):
#    pass

def vmax_method(absmag, appmag, c_dist, redshift, bins=100):
    """
    Implements the basic V_max method for getting the lum func.
    
    Arguments are the vectors of absolute magnitude, apparent magnitude
    comoving distance to each galaxy, and the redshift of each galaxy
    
    The argument goes like this:
    We weight each galaxy by the inverse of the total volume it could occupy
    while being observed. This volume is proportional to the maximum comoving 
    distance at which the object may be observed cubed.
    
    To find this maximum distance, we note that the fixed absolute mag of each 
    galaxy is M = m - mu(z,gal_properties), where gal_properties are used to
    get things like k_corrections and extinction etc.
    
    Thus mu = m - M, where mu is defined here as
    mu = 5log10(lum_dist) + 25 + k_cor + extinction
    
    At maximum distance, the galaxy will be as faint as can still be observed,
    denoted by m_max, so
    mu_max = m_max - M
    5log10(lum_dist_max) + 25 + k_cor + extinction = m_max - m+5log10(lum_dist_max) + 25 + k_cor + extinction
    5log10(lum_dist_max) = m_max - m + 5log10(lum_dist)
    lum_dist_max = 10**((m_max - m + 5log10(lum_dist))/5)
    
    Then the maximum comoving distance is given by lum_dist_max/(1+z)

    """
    #First we need to find zlim for each galaxy
    m_max = appmag.max()
    ldist = lum_dist(redshift, c_dist)
    lum_dist_max = 10 ** ((m_max - appmag + 5 * np.log10(ldist)) / 5.0)
    max_dist = lum_dist_max / (1 + redshift)

    weights = 1. / max_dist ** 3
    weights = weights / np.sum(weights)

    hist, edges = np.histogram(absmag, bins=bins, weights=weights, density=True, range=(-22, -16))

    M = (edges[1:] + edges[:-1]) / 2
    return hist, M

def absmagmax(maxmagr, appmag, absmag):
    """
    The DIMMEST an object can be at a given redshift/distance
    """
    return maxmagr - appmag + absmag

def absmagmin(minmagr, appmag, absmag):
    """
    The BRIGHTEST an object can be at a given redshift/distance
    """

    return minmagr - appmag + absmag



