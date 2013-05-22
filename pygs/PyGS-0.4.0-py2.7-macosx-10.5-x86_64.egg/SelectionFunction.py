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


import utils


##################################################################
# SelectionFunction class
##################################################################
class SelectionFunction(object):
    def __init__(self):
        pass


    def fit_selection_simple(self, bins=None):
        """
        Fits the simple selection function to the N-z relation
        
        Fits for A,g,t
        """
        from scipy.optimize import curve_fit


        if not bins:
            bins = utils.FD_bins(self.survey_data['redshift'])

        hist, edges = np.histogram(self.survey_data['redshift'], normed=True, bins=bins)

        centres = np.zeros(edges.shape[0] - 1)
        for i, edge in enumerate(edges):
            if i == len(edges) - 1:
                break
            centres[i] = (edge + edges[i + 1]) / 2.

        popt, pcov = curve_fit(self._selection_simple, xdata=centres, ydata=hist, p0=(0.95, 1.5, 0.085))

        #Return A,g,t

        print "PARAMETERS OF THE FIT AND THEIR STANDARD DEVIATION"
        print "A: ", popt[0], np.sqrt(pcov[0, 0])
        print "g: ", popt[1], np.sqrt(pcov[1, 1])
        print "t: ", popt[2], np.sqrt(pcov[2, 2])

        plt.clf()
        plt.hist(self.survey_data['redshift'], bins=bins, normed=True)
        plt.plot(centres, self._selection_simple(centres, popt[0], popt[1], popt[2]))
        plt.show()

        self.simple_selection_params = {'A':popt[0], 'g':popt[1], 't':popt[2]}
        print self.simple_selection_params

    def _selection_simple(self, z, A, g, t):
        """
        Definition of the simple selection function (thesis eq.2.10)
        """

        return A * (z ** g) * np.exp(-(z / t) ** g)


    def _selection_simple_integral(self, x, A, g, t):
        """
        Defines the integral of the simple selection function from 0 to x
        """

        import scipy.special as sp

        return A * (1 / t) ** (-1 - g) * (sp.gamma(1 / g) - g * sp.gamma(1 + 1 / g) * sp.gammaincc(1 + 1 / g, ((x / t) ** g))) / g ** 2

    def _s2_inv_cdf(self, z_max, A, g, t):
        """
        Interpolates the integral of the simple selection function as an inverse.
        """
        import scipy.interpolate as interp

        grid = np.linspace(0, z_max, 1000)


        icdf = interp.interp1d(self._selection_simple_integral(grid, A, g, t) / self._selection_simple_integral(z_max, A, g, t), grid)

        return icdf

    def create_radial_selection(self, N=None):
        """
        Creates a random catalogue of particles based on a defined selection function. Only radial co-ords.
        """

        z_min = self.survey_data['redshift'].min
        z_max = self.survey_data['redshift'].max

        #First make a fit to a histogram
        self.fit_selection_simple()

        #Generate some random numbers
        if N is None:
            N = self.N

        padded_N = 2 * N

        X = np.random.random(padded_N)

        #Generate the radii
        icdf = self._s2_inv_cdf(z_max, **self.simple_selection_params)
        radii = icdf(X)

        radii = radii[(radii > z_min) & (radii < z_max)]

        if len(radii) > N:
            radii = radii[1:N]
            return radii

        while len(radii) < N:
            X = np.random.random(N)
            new_radii = icdf(X)
            new_radii = new_radii[(radii > z_min) & (radii < z_max)]

            radii = np.append(radii, new_radii)

        radii = radii[1:N]

        plt.clf()
        plt.hist(self.survey_data['redshift'], bins=50)
        plt.hist(radii, bins=50)
        plt.show()

        return radii

    def do_selection_and_weighting(self):
        """
        Fits the simple selection function to the data and writes out weights to the data file for reading.
        """
        self.fit_selection_simple()

        weights = 1 / self._selection_simple(self.survey_data['redshift'], **self.simple_selection_params)  #Inverse selection function
        
        self.survey_data['weight'] = weights
        return
        
        
    def m_max(self):
        """
        calculates the maximum magnitude of a given redshift
        """
        
        self.survey_data['M_max'] = np.min(self.survey_data['mag_r']) - \
            5.0*np.log(self._LumDistance(self.survey_data['c_dist'])) - 25 - \
            self._KCorrect(self.survey_data["mag_g"] - self.survey_data["mag_r"])
        
        
    def m_min(self):
        """
        calculates the maximum magnitude of a given redshift
        """
        
        self.survey_data['M_min'] = np.max(self.survey_data['mag_r']) - \
            5.0*np.log(self._LumDistance(self.survey_data['c_dist'])) - 25 - \
            self._KCorrect(self.survey_data["mag_g"] - self.survey_data["mag_r"])
            
    def selection_from_lumfunc(self):
        """
        Calculates the selection function from the luminosity function
        """
        import scipy.integrate as intg
        
        if 'M_max' not in self.survey_data.columns:
            self.m_max()
        if 'M_min' not in self.survey_data.columns:
            self.m_min()
            
        lumfunc, M = self.EEP()

        ##### Get denominator ######
        # interpolate luminosity function
        lumfunction = spline(M, lumfunc, k=spline_order)        
        # re-grid Mag over bounds from fort function         
        M, dM = np.linspace(M[0], M[-1], 4097, retstep=True)
        #Re-grid lum function        
        lumfunc = lumfunction(M)
        #integrate
        denom  = intg.romb(lumfunc,dx=dM)
        
        numer = np.zeros_like(self.survey_data['redshift'])
        for i,z in enumerte(self.survey_data['redshift']):
            #find lower and upper limits of integration
            lower_limit = max(M[0], self.survey_data['M_min'][i])
            upper_limit = min(M[-1],self.survey_data['M_max'][i])

            #Re-grid Mag
            M, dM = np.linspace(lower_limit, upper_limit, 4097, retstep=True)
            lumfunc = lumfunction(M)
            
            numer[i] = intg.romb(lumfunc,dx=dM)
            
        self.survey_data['weights'] = numer/denom            
            
                        
