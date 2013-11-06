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

import fort.corr as corr
import cosmolopy.distance as cd
import SelectionFunction as sf


def _correlation_function_dd_wrapper(pos1, end_r, n_r, n_cores):
    """
    Simply a wrapper for the fortran correlation function routines
    """

    correlation = corr.correlation_dd(pos1=np.asfortranarray(pos1), end_r=end_r, nR=n_r, n_cores=n_cores)

    return correlation

def _correlation_function_dr_wrapper(pos1, pos2, end_r, n_r, n_cores):
    """
    Simply a wrapper for the fortran correlation function routines
    """

    correlation = corr.correlation_dr(pos1=np.asfortranarray(pos1),
                                      pos2=np.asfortranarray(pos2),
                                      end_r=end_r, nR=n_r, n_cores=n_cores)

    return correlation

def _correlation_1d_DD_wrapper(pos1, end_s, ns, n_cores):
    """ A wrapper for 1d correlation function routine """

    print pos1
    pos1 = np.sort(pos1)
    correlation = corr.correlation_dd_1d(ns, end_r=end_s, n=len(pos1), pos1=np.asfortranarray(pos1), n_cores=n_cores)

    return correlation

def _correlation_1d_DR_wrapper(pos1, pos2, end_s, ns, n_cores):
    """ A wrapper for 1d correlation function routine """

    pos1 = np.sort(pos1)
    pos2 = np.sort(pos2)
    correlation = corr.correlation_dr_1d(nr=ns, end_r=end_s , n=len(pos1), pos1=np.asfortranarray(pos1),
                                         n2=len(pos2), pos2=np.asfortranarray(pos2), n_cores=n_cores)

    print "got dr correlation: ", len(correlation), correlation
    return correlation

def _1d_correlation(pos, min_cut, max_cut, end_s=0.02, ns=15, n_randoms=1, n_cores=1):
    """
    Does a 1d correlation in either redshift or comoving distance space.
    """

    if pos.max() < 10.0:
        A, g, t = sf.fit_selection_simple_z(pos)
    else:
        A, g, t = sf.fit_selection_simple(pos)


    DD = _correlation_1d_DD_wrapper(pos1=pos, end_s=end_s, ns=ns, n_cores=n_cores)
    print "Done DD"
    RR = np.zeros((ns))
    DR = np.zeros((ns))
    print "made zeros"
    for i in range(n_randoms):
        rand_r = sf.create_radial_selection(A, g, t, min_cut, max_cut, len(pos))

        if i == 0:
            plt.hist(rand_r, normed=True)
            plt.hist(pos, normed=True)
            plt.show()

            go_ahead = str(raw_input("do you like what you see?? [Y/n]"))
            if go_ahead == 'n':
                raise ValueError("Okay we'll stop then")

        print len(rand_r)
        RR += _correlation_1d_DD_wrapper(pos1=rand_r, end_s=end_s, ns=ns, n_cores=n_cores)
        print "Done RR"
        DR += _correlation_1d_DR_wrapper(pos1=pos, pos2=rand_r, end_s=end_s, ns=ns, n_cores=n_cores)
        print "done DR"

    RR /= n_randoms
    DR /= n_randoms

    #Use the Landy-Szalay Estimator
    Corr = 1 + DD / RR - 2 * DR * (len(pos) - 1.0) / len(pos) / RR

    #Calculate the centre of bins
    s_bins = np.linspace(end_s / (2 * ns), end_s * (1 - 0.5 / ns), ns)

    print "got to the end..."
    print Corr
    return s_bins.copy(), Corr.copy()

def _correlation_in_s(quantity='c_dist', end_s=0.02, nr=15, n_randoms=1, n_cores=1):
    """
    The convenience (callable) function to perform a correlation function estimation in redshift/c_dist space
    
    Note: At this time it will perform the correlation either in redshift or in comoving distance, 
    but the final result will always be displayed in comoving distance. As many randoms as wanted can be 
    used. There are NO error estimates as yet. Also, the 'angular selection function' used is merely the
    exact angles of the original particles. The algorithm can be sped up by using sorted redshift - will 
    do this soon.
    
    PARAMETERS
    quantity  ['c_dist']    - Should be 'c_dist' or 'redshift'. Specifies how to bin the data.
    end_s     [0.02]        - The largest separation to calculate. Default 0.02 for z, 120 for s.
    nr        [15]          - The number of bins to use.
    n_randoms [1]           - The number of random catalogues to use.
    
    VALUES
    s_bins                  - an array of length nr with bin centres
    Corr                    - an array of length nr with correlation values.
    """
    #Do some default cleaning
    if quantity != 'c_dist' and quantity != 'redshift':
        quantity = 'c_dist'

    if quantity == 'c_dist' and end_s == 0.02:
        end_s = 120

    #Convert to cartesian
    real_pos = np.array(self.sph2car(self.survey_data[quantity], self.survey_data['ra'], self.survey_data['dec']))
    print "shape of real_pos, ", real_pos.shape

    #Calculate data-data pairs
    DD = self.correlation_function_dd_wrapper(real_pos, end_s, nr)

    RR = np.zeros((n_randoms, nr))
    DR = RR
    for i in range(n_randoms):
        print "Processing random number ", i
        #Make some randoms
        #Use the simple selection function production for now
        #Except I'll need an angle production as well. For now, use same angles as original.
        rand_r = self.create_radial_selection()
        random_pos = np.array(self.sph2car(rand_r, self.survey_data['ra'], self.survey_data['dec']))

        #For all randoms, calculate DR and RR pairs
        RR[i, :] = self.correlation_function_dd_wrapper(random_pos, end_s, nr)
        DR[i, :] = self.correlation_function_dr_wrapper(pos1=real_pos, pos2=random_pos, end_s=end_s, nr=nr)

    #Take the means along the n_randoms axis
    RR = np.mean(RR, axis=0)
    DR = np.mean(DR, axis=0)

    #Use the Landy-Szalay Estimator
    Corr = 1 + DD / RR - 2 * DR / RR

    #Calculate the centre of bins
    s_bins = np.linspace(end_s / (2 * nr), end_s * (1 - 0.5 / nr), nr)

    if quantity == 'redshift':
        s_bins = cd.comoving_distance(s_bins, **self.cosmology)

    #Plot the function
    plt.clf()
    plt.plot(s_bins, Corr)
    plt.show()
    plt.savefig(self.__correlation_dir + '/correlation_in_' + quantity + '.eps')

    plt.clf()
    plt.plot(s_bins, s_bins ** 2 * Corr)
    plt.show()
    plt.savefig(self._correlation_dir + '/correlation_in_' + quantity + '_by_s_squared.eps')

    return s_bins, Corr
