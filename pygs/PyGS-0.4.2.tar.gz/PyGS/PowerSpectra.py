'''
Created on Dec 3, 2012

@author: Steven
'''
#==============================================================================
# Imports
#==============================================================================
import sys

try:
    import matplotlib.pyplot as plt
except:
    sys.exit("Please install Matplotlib")

try:
    import numpy as np
except:
    sys.exit("Please install Numpy")

try:
    from scipy.interpolate import griddata
except:
    sys.exit("Please install scipy")
    
import utils
try:
    from fort.DFT import dft
    fort_routines = True
except:
    print "Warning: DFT fortran routines not found"
    fort_routines = False
    

#==============================================================================
# Functions
#==============================================================================

def power_spec_1d_fast(quantity, bins=None, min_wave=0.0001, 
                       max_wave=0.02, pad=1, weight=None):
    """
    Computes the 1D power spectrum and plots it.
    
    This method uses the numpy fft algorithm to calculate the real to real 
    DFT of any quantity in the GS data, then converts this to a power
    spectrum (merely squares it). As such, it needs what I call 'density 
    values' as its input, which here are merely histogram values. It will 
    only calculate as many DFT points as there are bins in the histogram, 
    which is fine for frequency-based plots, but makes wavelength (inverse 
    frequency) plots very angular. To increase the number of points you can
    pad the original data with zeroes on either end, but even this does not
    ensure a smooth wavelength plot. To get a very nice looking wavelength 
    plot, use PowerSpec_1d_slow().
    
    
    INPUT PARAMETERS:
    quantity                  : the quantity type used for the dft. Generally 'redshift', 'c_dist', 'ra' or 'dec'
    bins        [None]        : the number of bins to use in the histogram to get 'densities'. 
                                If none, an 'optimal' bin number is used.
    min_wave    [0.0001]      : The minimum wavelength to plot.
    max_wave    [0.02]        : The maximum wavelength to plot
    pad         [1]           : How much the original data length is multiplied by (zeroes padded in the extra space).
                                The higher the padding, the longer the calculation, but the better the resolution.
    wavelength  [True]        : Whether to plot the power against wavelength. If False, plots against frequency.
    weight      [None]        :  An optional setting allowing a further weight to be applied to the bin densities before calculation.
                                0 - No extra weighting (each bin will be its number)
                                'weights_1' - Inverse of selection function (simple)
                                'weights_2' - Inverse of selection function +1 (simple)
    
    OUTPUT PARAMETERS:
    ps                        : array of power spectrum values
    freq                      : array of frequencies
    wvl                       : array of wavelengths
    """

    # First bin the quantity (higher number of bins tends towards phase calculation)
    if not bins:
        bins = utils.FD_bins(quantity)

    if weight:
        hist, edges = np.histogram(quantity, bins, 
                                   weights=weight)
    else:
        hist, edges = np.histogram(quantity, bins)

    #Calculate stepsize.
    step = edges[2] - edges[1]
     
    n = pad * hist.size
    ps = np.abs(np.fft.rfft(hist, n=n) / np.sqrt(n)) ** 2
    
    freq = np.fft.fftfreq(n, step)

    wavelength = 1.0 / freq[:np.floor(n / 2 + 1)]

    return ps, freq * 2.0 * np.pi, wavelength


def power_spec_1d_slow(quantity, bins=None, min_wave=0.0001, max_wave=0.02, n_waves=1000, weight=None):
    """
    Computes the 1D power spectrum and plots it.
    
    This method uses a slower DFT method, rather than an FFT. However, the bonus is that the increments in
    wavelength are regular and completely customizable (producing smooth plots). And also can do weights.
    
    INPUT PARAMETERS
    quantity    ['redshift']    : the quantity to analyse.
    bins        [None]          : the number of bins to use in the histogram , if None, performs a 'phase'
                                    DFT, which is to say each data point counts for 1.0 at its precise location.
    min_wave    [0.0001]        :the minimum wavelength to calculate
    max_wave    [0.02]        :the maximum wavelength ot calculate
    n_waves     [1000]          :the number of wavelengths to calculate
    
    OUTPUT PARAMETERS
    ps    : the power spectrum
    wvl   : the wavelengths
    """
    #Get an equally-spaced array of wavelengths
    wavelengths = np.asfortranarray(np.linspace(min_wave, max_wave, n_waves))
    freq = 2*np.pi / wavelengths
    #If a number of bins is given then bin it up and do it faster, if not, do "phase" calc
    if bins:
        if weight:
            hist, edges = np.histogram(quantity, bins, 
                                       weights=weight)
        else:
            hist, edges = np.histogram(quantity, bins)

        centres = np.asfortranarray(edges[:-1] + (edges[1]-edges[0])/2.0)
        ps = dft.dft_one(np.asfortranarray(hist), centres, wavelengths)
    
    else:
        if not weight:
            ps = dft.phasedft_one(np.asfortranarray(quantity), wavelengths)
        else:
            ps = dft.dft_one(np.asfortranarray(weight), 
                             np.asfortranarray(quantity), 
                             wavelengths)

    return ps, freq,wavelengths

#    def PowerSpec_2d_fast(self, quantity=("c_dist", "ra"), bins=None, min_wave=(0.0001, 0.0001), max_wave=(1000.0, 1000.0),
#                     pad=(1, 1), wavelength=True):
#        """
#        Returns and plots the 2d power spectra of the given quantities
#        
#        This is the equivalent procedure to PowerSpec_1d_fast for 2-dimensions. However, in this case,
#        the plotting becomes more difficult. The default plots are density images, with colours showing
#        peaks. The irregular nature of the wavelength plots is pronounced in 2D however. 
#        
#        To produce the wavelength plots, a regular grid is created and the original power spectrum
#        is interpolated onto it. This produces very striated plots however. To get nice plots in 
#        wavelength, use PowerSpec_2d_slow().
#        
#        INPUT PARAMETERS
#        quantity (tuple) [('c_dist','ra')]    :the quantities to use on (x,y) axes.
#        bins (int)        [None]              : the number of bins to use in both directions
#        min_wave (tuple)    [(0.0001,0.0001)] : the minimum wavelengths to use
#        max_wave (tuple)    [(1000.0,1000.0)] :the maximum wavelengths to use.
#        pad      (tuple)    [(1,1)]            :the factor use for padding with zeroes.
#        wavelength (bool)    [True]            :whether to plot against wavelength
#        
#        OUTPUT PARAMETERS
#        cps    : the 2D power spectrum in the range given
#        cfreq1 : the frequencies in the first quantity
#        cfreq2 : the frequencies in the second quantity
#        wvl1   : the wavelengths in the first quantity
#        wvl2   : the wavlengths in the second quantity
#        
#        """
#
#
#        # First bin the quantity (higher number of bins tends towards phase calculation)
#        if not bins:
#            bins = [np.ceil(np.sqrt(self.N / 100)), np.ceil(np.sqrt(self.N / 100))]
#            if bins[0] < 30:
#                bins = [30, 30]
#
#        if quantity is 'c_dist' and min_wave == 0.0001 and max_wave == 0.02:
#            min_wave = 10
#            max_wave = 180
#        elif quantity is 'ra' and min_wave == 0.0001 and max_wave == 0.02:
#            min_wave = 0.01
#            max_wave = 2 * np.pi
#        elif quantity is 'dec' and min_wave == 0.0001 and max_wave == 0.02:
#            min_wave = 0.01
#            max_wave = np.pi
#
#        hist = np.histogram2d(self.survey_data[quantity[0]], self.survey_data[quantity[1]], bins)
#
#        n1 = pad[0] * (hist[1].size - 1)
#        n2 = pad[1] * (hist[2].size - 1)
#
#        ps = np.abs(np.fft.rfft2(hist[0], s=(n1, n2)) / np.sqrt(n1 * n2)) ** 2
#
#        ps = ps[np.floor(n1 / 2 + 1):, 1:]
#
#        step1 = hist[1][2] - hist[1][1]
#        step2 = hist[2][2] - hist[2][1]
#
#        freq1 = np.fft.fftfreq(n1, step1)
#        freq2 = np.fft.fftfreq(n2, step2)
#        freq1 = freq1[1:np.floor(n1 / 2)]
#        freq2 = freq2[1:np.floor(n2 / 2)]
#
#        wavelength1 = 1.0 / freq1
#        wavelength2 = 1.0 / freq2
#
#        condition_1 = (wavelength1 < max_wave[0]) & (wavelength1 > min_wave[0])
#        condition_2 = (wavelength2 < max_wave[1]) & (wavelength2 > min_wave[1])
#
#
#        wvl1 = wavelength1[condition_1]
#        wvl2 = wavelength2[condition_2]
#        cfreq1 = 2.0 * np.pi * freq1[condition_1]
#        cfreq2 = 2.0 * np.pi * freq2[condition_2]
#
#        cps = ps[condition_1, :]
#        cps = cps[:, condition_2]
#
#        if not wavelength:
#            plt.clf()
#            plt.title("2D P.S. for " + quantity[0] + "and " + quantity[1] + " of sample " + self.sample_name.partition('.')[0] + " from " + self.survey_name)
#            plt.imshow(cps, interpolation="gaussian", aspect=np.max(cfreq1) / np.max(cfreq2), extent=(np.min(cfreq1), np.max(cfreq1), np.min(cfreq2), np.max(cfreq2)))
#            plt.xlabel(quantity[0] + " frequency")
#            plt.ylabel(quantity[1] + " frequency")
#            plt.show()
#            plt.savefig(self._power2d_dir + '/' + quantity[0] + 'AND' + quantity[1] + '_bins' + str(bins[0]) + ',' + str(bins[1]) + '_pad' + str(pad[0]) + ',' + str(pad[1]) + '_frequency.eps')
#
#        else:
#            grid_1, grid_2 = np.mgrid[np.min(wvl1):np.max(wvl1):300j, np.min(wvl2):np.max(wvl2):300j]
#            points = np.zeros((wvl2.size * wvl1.size, 2))
#            for i, wv in enumerate(wvl2):
#                points[i * wvl1.size:(i + 1) * wvl1.size, 0] = wvl1
#            for i, wv in enumerate(wvl2):
#                points[i * wvl1.size:(i + 1) * wvl1.size, 1] = wv
#
#            print wvl2.size * wvl1.size
#            print cps.size
#            grid_z0 = griddata(points, np.reshape(cps, (wvl1.size * wvl2.size)), (grid_1, grid_2), method='linear')
#
#            plt.title("2D P.S. for " + quantity[0] + "and " + quantity[1] + " of sample " + self.sample_name.partition('.')[0] + " from " + self.survey_name)
#            plt.imshow(grid_z0.T, interpolation="gaussian", aspect=np.max(wvl1) / np.max(wvl2), origin='lower', extent=(np.min(wvl1), np.max(wvl1), np.min(wvl2), np.max(wvl2)))
#            if quantity == 'redshift':
#                plt.xlabel(quantity[0] + "Wavelength, (z)")
#                plt.xlabel(quantity[1] + "Wavelength, (z)")
#            elif quantity == 'c_dist':
#                plt.xlabel(quantity[0] + r'Wavelength, $Mpc h^{-1}$s')
#                plt.xlabel(quantity[1] + r'Wavelength, $Mpc h^{-1}$s')
#
#            plt.show()
#            plt.savefig(self._dirs['PowerSpecs_2D'] + quantity[0] + 'AND' + quantity[1] + '_bins' + str(bins[0]) + ',' + str(bins[1]) + '_pad' + str(pad[0]) + ',' + str(pad[1]) + '_frequency.eps')
#
#        return cps, cfreq1, cfreq2, wvl1, wvl2
#
#    def PowerSpec_2d_slow(self, quantity=("c_dist", "ra"), bins=None, min_wave=(0.0001, 0.0001), max_wave=(1000.0, 1000.0), n_waves=(1000, 1000)):
#        """
#        Returns and plots the 2d power spectra of the given quantities
#        
#        This is the equivalent procedure to PowerSpec_1d_fast for 2-dimensions. However, in this case,
#        the plotting becomes more difficult. The default plots are density images, with colours showing
#        peaks. The irregular nature of the wavelength plots is pronounced in 2D however. 
#        
#        To produce the wavelength plots, a regular grid is created and the original power spectrum
#        is interpolated onto it. This produces very striated plots however. To get nice plots in 
#        wavelength, use PowerSpec_2d_slow().
#        
#        INPUT PARAMETERS
#        quantity (tuple) [('c_dist','ra')]    :the quantities to use on (x,y) axes.
#        bins (int)        [None]              : the number of bins to use in both directions, if none, do phase.
#        min_wave (tuple)    [(0.0001,0.0001)] : the minimum wavelengths to use
#        max_wave (tuple)    [(1000.0,1000.0)] :the maximum wavelengths to use.
#        n_waves  (tuple)    [(1000,1000)]     : the number of wavlengths to use.
#        wavelength (bool)    [True]            :whether to plot against wavelength
#        
#        OUTPUT PARAMETERS
#        ps    : the 2D power spectrum in the range given
#        wvl1   : the wavelengths in the first quantity
#        wvl2   : the wavlengths in the second quantity
#        
#        """
#
#        wvl1 = np.asfortranarray(np.linspace(min_wave[0], max_wave[0], n_waves[0]))
#        wvl2 = np.asfortranarray(np.linspace(min_wave[1], max_wave[1], n_waves[1]))
#
#        # First bin the quantity (higher number of bins tends towards phase calculation)
#        if bins:
#            hist, x_edges, y_edges = np.histogram2d(self.survey_data[quantity[0]], self.survey_data[quantity[1]], bins)
#            x_centres = []
#            for i, edge in enumerate(x_edges[:-1]):
#                x_centres = x_centres + [(edge + x_edges[i + 1]) / 2]
#            y_centres = []
#            for i, edge in enumerate(y_edges[:-1]):
#                y_centres = y_centres + [(edge + y_edges[i + 1]) / 2]
#            x_centres = np.asfortranarray(x_centres)
#            y_centres = np.asfortranarray(y_centres)
#
#            ps = dft.dft_two(np.asfortranarray(hist), x_centres, y_centres, wvl1, wvl2)
#        else:
#            ps = dft.phasedft_two(np.asfortranarray(self.survey_data[quantity[0]]), np.asfortranarray(self.survey_data[quantity[1]]),
#                                  wvl1, wvl2)
#
#
#        plt.title("2D P.S. for " + quantity[0] + "and " + quantity[1] + " of sample " + self.sample_name.partition('.')[0] + " from " + self.survey_name)
#        plt.imshow(ps.T, interpolation="gaussian", aspect=np.max(wvl1) / np.max(wvl2), origin='lower', extent=(np.min(wvl1), np.max(wvl1), np.min(wvl2), np.max(wvl2)))
#        if quantity == 'redshift':
#            plt.xlabel(quantity[0] + "Wavelength, (z)")
#            plt.xlabel(quantity[1] + "Wavelength, (z)")
#        elif quantity == 'c_dist':
#            plt.xlabel(quantity[0] + r'Wavelength, $Mpc h^{-1}$s')
#            plt.xlabel(quantity[1] + r'Wavelength, $Mpc h^{-1}$s')
#        plt.show()
#        plt.savefig(self._dirs['PowerSpecs_2D'] + quantity[0] + 'AND' + quantity[1] + '_bins' + str(bins[0]) + ',' + str(bins[1]) + '_frequency_smooth.eps')
#
#        return ps, wvl1, wvl2
#
#    def PowerSpec_3d_fast(self, quantity=("c_dist", "ra", "dec"), bins=None, min_wave=(0.0001, 0.0001, 0.0001),
#                          max_wave=(1000.0, 1000.0, 1000.0), pad=(1, 1, 1), wavelength=False):
#        """
#        Returns and plots the 2d power spectra of the given quantities
#        
#        At the moment this does not work correctly. This will be fixed soon.
#        
#        This is the equivalent procedure to PowerSpec_1d_fast for 2-dimensions. However, in this case,
#        the plotting becomes more difficult. The default plots are density images, with colours showing
#        peaks. The irregular nature of the wavelength plots is pronounced in 2D however. 
#        
#        To produce the wavelength plots, a regular grid is created and the original power spectrum
#        is interpolated onto it. This produces very striated plots however. To get nice plots in 
#        wavelength, use PowerSpec_2d_slow().
#        
#        INPUT PARAMETERS
#        quantity (tuple) [('c_dist','ra')]    :the quantities to use on (x,y) axes.
#        bins (int)        [None]              : the number of bins to use in both directions
#        min_wave (tuple)    [(0.0001,0.0001)] : the minimum wavelengths to use
#        max_wave (tuple)    [(1000.0,1000.0)] :the maximum wavelengths to use.
#        pad      (tuple)    [(1,1)]            :the factor use for padding with zeroes.
#        wavelength (bool)    [True]            :whether to plot against wavelength
#        
#        OUTPUT PARAMETERS
#        cps    : the 2D power spectrum in the range given
#        cfreq1 : the frequencies in the first quantity
#        cfreq2 : the frequencies in the second quantity
#        wvl1   : the wavelengths in the first quantity
#        wvl2   : the wavlengths in the second quantity
#        
#        """
#
#
#        # First bin the quantity (higher number of bins tends towards phase calculation)
#        if not bins:
#            bins = np.array([np.ceil(np.sqrt(self.N / 100)), np.ceil(np.sqrt(self.N / 100)), np.ceil(np.sqrt(self.N / 100))])
#            if bins[0] < 30:
#                bins = np.array([30, 30, 30])
#        print bins.shape
#        print self.survey_data[quantity[0]]
#        hist, x_edges, y_edges, z_edges = np.histogramdd([self.survey_data[quantity[0]], self.survey_data[quantity[1]], self.survey_data[quantity[2]]], bins)
#
#        n1 = pad[0] * (x_edges.size - 1)
#        n2 = pad[1] * (y_edges.size - 1)
#        n3 = pad[2] * (z_edges.size - 1)
#
#        ps = np.abs(np.fft.rfftn(hist, s=(n1, n2, n3)) / np.sqrt(n1 * n2 * n3)) ** 2
#
#        ps = ps[np.floor(n1 / 2 + 1):, np.floor(n2 / 2 + 1):, 1:]
#
#        step1 = x_edges[2] - x_edges[1]
#        step2 = y_edges[2] - y_edges[1]
#        step3 = z_edges[2] - z_edges[1]
#
#        freq1 = np.fft.fftfreq(n1, step1)
#        freq2 = np.fft.fftfreq(n2, step2)
#        freq3 = np.fft.fftfreq(n3, step3)
#        freq1 = freq1[1:np.floor(n1 / 2)]
#        freq2 = freq2[1:np.floor(n2 / 2)]
#        freq3 = freq3[1:np.floor(n3 / 2)]
#
#        wavelength1 = 1.0 / freq1
#        wavelength2 = 1.0 / freq2
#        wavelength3 = 1.0 / freq3
#
#        condition_1 = (wavelength1 < max_wave[0]) & (wavelength1 > min_wave[0])
#        condition_2 = (wavelength2 < max_wave[1]) & (wavelength2 > min_wave[1])
#        condition_3 = (wavelength3 < max_wave[2]) & (wavelength3 > min_wave[2])
#
#
#        wvl1 = wavelength1[condition_1]
#        wvl2 = wavelength2[condition_2]
#        wvl3 = wavelength3[condition_3]
#        cfreq1 = 2.0 * np.pi * freq1[condition_1]
#        cfreq2 = 2.0 * np.pi * freq2[condition_2]
#        cfreq3 = 2.0 * np.pi * freq2[condition_3]
#
#        cps = ps[condition_1, :, :]
#        cps = cps[:, condition_2, :]
#        cps = cps[:, :, condition_3]
#
#        return cps, cfreq1, cfreq2, cfreq3, wvl1, wvl2 , wvl3
#
#    def PowerSpec_3d_slow(self, quantity=("c_dist", "ra", "dec"), bins=None, min_wave=(0.0001, 0.0001, 0.0001),
#                          max_wave=(1000.0, 1000.0, 1000.0), n_waves=(1000, 1000, 1000)):
#        """
#        Returns and plots the 2d power spectra of the given quantities
#        
#        This is the equivalent procedure to PowerSpec_1d_fast for 2-dimensions. However, in this case,
#        the plotting becomes more difficult. The default plots are density images, with colours showing
#        peaks. The irregular nature of the wavelength plots is pronounced in 2D however. 
#        
#        To produce the wavelength plots, a regular grid is created and the original power spectrum
#        is interpolated onto it. This produces very striated plots however. To get nice plots in 
#        wavelength, use PowerSpec_2d_slow().
#        
#        INPUT PARAMETERS
#        quantity (tuple) [('c_dist','ra')]    :the quantities to use on (x,y) axes.
#        bins (int)        [None]              : the number of bins to use in both directions, if none, do phase.
#        min_wave (tuple)    [(0.0001,0.0001)] : the minimum wavelengths to use
#    
#            
#        """
#
#        wvl1 = np.asfortranarray(np.linspace(min_wave[0], max_wave[0], n_waves[0]))
#        wvl2 = np.asfortranarray(np.linspace(min_wave[1], max_wave[1], n_waves[1]))
#        wvl3 = np.asfortranarray(np.linspace(min_wave[2], max_wave[2], n_waves[2]))
#
#        # First bin the quantity (higher number of bins tends towards phase calculation)
#        if bins:
#            hist, x_edges, y_edges, z_edges = np.histogramdd(self.survey_data[quantity[0]], self.survey_data[quantity[1]], self.survey_data[quantity[2]], bins)
#            x_centres = []
#            for i, edge in enumerate(x_edges[:-1]):
#                x_centres = x_centres + [(edge + x_edges[i + 1]) / 2]
#            y_centres = []
#            for i, edge in enumerate(y_edges[:-1]):
#                y_centres = y_centres + [(edge + y_edges[i + 1]) / 2]
#            z_centres = []
#            for i, edge in enumerate(z_edges[:-1]):
#                z_centres = z_centres + [(edge + z_edges[i + 1]) / 2]
#            x_centres = np.asfortranarray(x_centres)
#            y_centres = np.asfortranarray(y_centres)
#            z_centres = np.asfortranarray(z_centres)
#
#            ps = dft.dft_three(np.asfortranarray(hist), x_centres, y_centres, z_centres, wvl1, wvl2, wvl3)
#        else:
#            ps = dft.phasedft_two(np.asfortranarray(self.survey_data[quantity[0]]), np.asfortranarray(self.survey_data[quantity[1]]),
#                                  np.asfortranarray(self.survey_data[quantity[2]]), wvl1, wvl2, wvl3)
#
#
#        return ps, wvl1, wvl2, wvl3
#
#    #def filtering(self,quantity=['c_dist'],kmin=[35.0],kmax=[45.0],n_k=[10],min_phase=0.5):
#    #    """
#    #    Filters the galaxies based on whether they are in phase with a selected Fourier peak.
#    #
#    #    SHOULD BE ABLE TO DO ALL ANALYSIS WITH THE FILTERED GALAXIES BASED ON REMAINS CONDITION
#    #    IS IT BETTER TO DO THIS BY WRITING OUT THE 'FILTERED SURVEY'?
#    #    """
#    #
#    #    from PyGS.fort.filter import filters
#    #    if type(quantity) == type([1,2,3]):
#    #        dim = len(quantity)
#    #        if dim > 3:
#    #            sys.exit("Too many quantities in filter (must be 3 or less)")
#    #        if (len(kmin) != dim) or (len(kmax) != dim) or (len(n_k) !=dim):
#    #            sys.exit("All input values must have same dimension")
#    #
#    #    if dim == 1:
#    #        filters.filter_1d(self.survey_data[quantity[0]],kmin[0],kmax[0],n_k[0],min_phase)
#    #        self.remains = np.asfortranarray(filters.remains)
#    #
#    #        filter_file = open(self.filtered_dir+'/1D_filter_'+kmin[0]+'to'+kmax[0])
#    #        filter_file.write("# Fourier filter with following characteristics:\n")
#    #        filter_file.write("# kmin: "+kmin[0]+'\n')
#    #        filter_file.write("# kmax: "+ kmax[0]+'\n')
#    #        filter_file.write("# n_k: "+ n_k[0]+'\n')
#    #        filter_file.write("#======================")
#    #
#    #        atab.write(self.survey_data[self.remains],filter_file)
#    #
#    #        filter_file.close()
#    #
#    #    if dim == 3:
#    #        filters.filter_3d(self.survey_data[quantity[0],quantity[1],quantity[2]],kmin,kmax,n_k,min_phase)
#    #        self.remains = np.asfortranarray(filters.remains)
#    #
#    #    filter_file = open(self.filtered_dir+'/'+dim+'D_filter_'+kmin[0])
#    #    survey_file.write("# Omega_k: "+str(self.cosmology["omega_k_0"])+'\n')
#    #    survey_file.write("# h: "+str(self.cosmology["h"])+'\n')
#    #    survey_file.write("# =================================\n\n")
#
#    #  atab.write(self.survey_data,survey_file)
#
#    #  survey_file.close()
