'''
Created on Dec 3, 2012

@author: Steven
'''
##################################################################
# IMPORTS
##################################################################
import sys

try:
    import matplotlib.pyplot as plt
except:
    sys.exit("Please install Matplotlib")

try:
    import numpy as np
except:
    sys.exit("Please install Numpy")

from scipy.optimize import curve_fit
import scipy.special as sp
from scipy.interpolate import InterpolatedUnivariateSpline as spline
import scipy.integrate as integ
import utils


##################################################################
# SelectionFunction
##################################################################
def fit_selection_simple(cdist, bins=None, verbose=True):
    """
    Fits the simple selection function to the N-d relation
    
    Fits for A,g,t
    """

    if not bins:
        bins = utils.FD_bins(cdist)

    hist, edges = np.histogram(cdist, normed=True, bins=bins)
    centres = edges[:-1] + (edges[1] - edges[0]) / 2.0

    popt, pcov = curve_fit(selection_simple, xdata=centres, ydata=hist, p0=(0.95, 2.0, 340.0))

    if verbose:
        print "PARAMETERS OF THE FIT AND THEIR STANDARD DEVIATION"
        print "A: ", popt[0]  #, np.sqrt(pcov[0, 0])
        print "g: ", popt[1]  #, np.sqrt(pcov[1, 1])
        print "t: ", popt[2]  #, np.sqrt(pcov[2, 2])



    #Return A,g,t
    return popt[0], popt[1], popt[2]

def fit_selection_simple_z(redshifts, bins=None, verbose=True):
    """
    Fits the simple selection function to the N-d relation
    
    Fits for A,g,t
    """

    if not bins:
        bins = utils.FD_bins(redshifts)

    hist, edges = np.histogram(redshifts, normed=True, bins=bins)
    centres = edges[:-1] + (edges[1] - edges[0]) / 2.0

    popt, pcov = curve_fit(selection_simple, xdata=centres, ydata=hist, p0=(0.95, 2.0, 0.1))

    if verbose:
        print "PARAMETERS OF THE FIT AND THEIR STANDARD DEVIATION"
        print "A: ", popt[0]  #, np.sqrt(pcov[0, 0])
        print "g: ", popt[1]  #, np.sqrt(pcov[1, 1])
        print "t: ", popt[2]  #, np.sqrt(pcov[2, 2])

    #Return A,g,t
    return popt[0], popt[1], popt[2]

def selection_simple(z, A, g, t):
    """
    Definition of the simple selection function (thesis eq.2.10)
    
    Original from Baugh, C., & Efstathiou, G. 1993, MNRAS, 265, 145
    Also in Percival, W. et. al. 2007 APJ, 657, 645
    """

    return A * (z ** 2) * np.exp(-(z / t) ** g)

def get_sel_from_nd(A, g, t):
    #The volume element at a single point in r for a sphere is 4pi*r^2
    #We absorb the constant 4pi into the normalisation for simplicity
    #The normalisation is done so that at d = 0, S(d) = 1 (but this is arbitrary)
    norm = selection_simple(0.001, A, g, t) / 0.001 ** 2
    return lambda d: selection_simple(d, A, g, t) / (norm * d ** 2)

def selection_simple_integral(x, A, g, t):
    """
    Defines the integral of the simple selection function from 0 to x
    """

    return A * (1 / t) ** (-1 - g) * (sp.gamma(1 / g) - g * sp.gamma(1 + 1 / g) * sp.gammaincc(1 + 1 / g, ((x / t) ** g))) / g ** 2


def simple_inv_cdf(z_max, A, g, t):
    """
    Interpolates the integral of the simple selection function as an inverse.
    """
    grid = np.linspace(0, z_max, 1000)

    print selection_simple_integral(grid, A, g, t)[:50]
    print selection_simple_integral(z_max, A, g, t)
    icdf = spline(selection_simple_integral(grid, A, g, t) / selection_simple_integral(z_max, A, g, t), grid)

    return icdf

def create_radial_selection_simple(A, g, t, z_min, z_max, N):
    """
    Creates a random catalogue of particles based on a defined selection function. Only radial co-ords.
    """

    #First make a fit to a histogram
    #A, g, t = fit_selection_simple()

    padded_N = 2 * N

    X = np.random.random(padded_N)

    #Generate the radii
    icdf = simple_inv_cdf(z_max, A, g, t)
    radii = icdf(X)


    radii = radii[(radii > z_min) & (radii < z_max)]

    if len(radii) > N:
        radii = radii[1:N]
        return radii

    while len(radii) < N:
        print "in while loop"
        X = np.random.random(N)
        print len(X)
        new_radii = icdf(X)
        print len(new_radii)
        new_radii = new_radii[np.logical_and(radii > z_min, radii < z_max)]
        print len(new_radii)
        radii = np.append(radii, new_radii)
        print len(radii)
    radii = radii[1:N]

    #plt.clf()
    #plt.hist(radii, bins=50)
    #plt.show()

    return radii

def create_mock(s_of_z, zmin, zmax, N):

    #find max y
    maxval = np.max(np.exp(s_of_z(np.linspace(zmin, zmax, 1000))))

    #create random square
    x = np.random.rand(N) * (zmax - zmin) + zmin
    y = np.random.rand(N) * (maxval * 1.01)

    #find s at z
    z = np.exp(s_of_z(x))

    #get rid of large values
    redshifts = x[y < z]

    #based on cut fraction, make plenty of random vals
    gens = 1.3 * np.ceil(float(N) / len(redshifts)) * N

    #while len(redshifts) < N:
    #create random square
    x = np.random.rand(gens) * (zmax - zmin) + zmin
    y = np.random.rand(gens) * (maxval * 1.01)

    #find s at z
    z = np.exp(s_of_z(x))

    #get rid of large values
    redshifts = np.concatenate((redshifts, x[y < z]))

    #trim down to desired N
    redshifts = redshifts[:N]
    return redshifts

def selection_of_galaxies(phi, Mbins, apmag, absmag):
    """Generates a selection function value for each galaxy"""

    #First get the denominator
    cum_int = np.zeros_like(phi)
    for i in range(len(phi))[1:]:
        cum_int[i] = integ.simps(phi[:i], dx=Mbins[1] - Mbins[0])

    denom = cum_int[-1]

    #The max/min absmag of each galaxy at its redshift
    M_max = apmag.max() - apmag + absmag
    M_min = apmag.min() - apmag + absmag

    #Check which absmag values are inside calculated lumfunc range
    mask_valid = np.logical_and(absmag < Mbins[-1], absmag > Mbins[0])

    #The integral to the upper limit and lower limit for each galaxy
    sel_upper = np.zeros(len(M_max))
    sel_lower = np.zeros(len(M_max))

    #The upper limit is by default denom
    sel_upper[M_max >= Mbins[-1]] = denom

    #Create a spline fit to the cumulative integral
    fit = spline(Mbins, cum_int, k=2)


    sel_upper[np.logical_and(M_max < Mbins[-1], mask_valid)] = fit(M_max[np.logical_and(M_max < Mbins[-1], mask_valid)])
    sel_lower[np.logical_and(M_min > Mbins[0], mask_valid)] = fit(M_min[np.logical_and(M_min > Mbins[0], mask_valid)])

    total = (sel_upper - sel_lower) / denom
    #Make sure invalid values are set to nan
    total[np.logical_not(mask_valid)] = np.nan

    return total

def selection_of_z(sel_bins, phi, Mbins, apmag, absmag, redshift):
    """
    Get selection function of redshift only
    
    Returns a function of z which gives the log of the selection function.
    """

    #First get the denominator
    cum_int = np.zeros_like(phi)
    for i in range(len(phi))[1:]:
        cum_int[i] = integ.simps(phi[:i], dx=Mbins[1] - Mbins[0])

    fit = spline(Mbins, cum_int, k=2)
    denom = cum_int[-1]

    #The max/min absmag of each galaxy at its redshift
    M_max = apmag.max() - apmag + absmag
    M_min = apmag.min() - apmag + absmag

    dz = (redshift.max() - redshift.min()) / sel_bins

    sel = np.zeros(sel_bins)
    centres = np.zeros(sel_bins)
    for i in range(sel_bins):
        mask = np.logical_and(redshift > redshift.min() + i * dz,
                              redshift < redshift.max() + (i + 1) * dz)
        centres[i] = redshift.min() + (i + 0.5) * dz
        mmax = np.mean(M_max[mask])
        mmin = np.mean(M_min[mask])
        #if mmax < Mbins[-1] and mmin > Mbins[0]:
        sel[i] = (fit(mmax) - fit(mmin)) / denom
     #   else:
      #      sel[i] = np.nan

    selfunc = spline(centres, np.log(sel), k=2)
    return selfunc
#    def m_max(self):
#        """
#        calculates the maximum magnitude of a given redshift
#        """
#
#        self.survey_data['M_max'] = np.min(self.survey_data['mag_r']) - \
#            5.0*np.log(self._LumDistance(self.survey_data['c_dist'])) - 25 - \
#            self._KCorrect(self.survey_data["mag_g"] - self.survey_data["mag_r"])
#
#
#    def m_min(self):
#        """
#        calculates the maximum magnitude of a given redshift
#        """
#
#        self.survey_data['M_min'] = np.max(self.survey_data['mag_r']) - \
#            5.0*np.log(self._LumDistance(self.survey_data['c_dist'])) - 25 - \
#            self._KCorrect(self.survey_data["mag_g"] - self.survey_data["mag_r"])
#
#    def selection_from_lumfunc(self):
#        """
#        Calculates the selection function from the luminosity function
#        """
#        import scipy.integrate as intg
#
#        if 'M_max' not in self.survey_data.columns:
#            self.m_max()
#        if 'M_min' not in self.survey_data.columns:
#            self.m_min()
#
#        lumfunc, M = self.EEP()
#
#        ##### Get denominator ######
#        # interpolate luminosity function
#        lumfunction = spline(M, lumfunc, k=spline_order)
#        # re-grid Mag over bounds from fort function
#        M, dM = np.linspace(M[0], M[-1], 4097, retstep=True)
#        #Re-grid lum function
#        lumfunc = lumfunction(M)
#        #integrate
#        denom  = intg.romb(lumfunc,dx=dM)
#
#        numer = np.zeros_like(self.survey_data['redshift'])
#        for i,z in enumerte(self.survey_data['redshift']):
#            #find lower and upper limits of integration
#            lower_limit = max(M[0], self.survey_data['M_min'][i])
#            upper_limit = min(M[-1],self.survey_data['M_max'][i])
#
#            #Re-grid Mag
#            M, dM = np.linspace(lower_limit, upper_limit, 4097, retstep=True)
#            lumfunc = lumfunction(M)
#
#            numer[i] = intg.romb(lumfunc,dx=dM)
#
#        self.survey_data['weights'] = numer/denom
#
#
