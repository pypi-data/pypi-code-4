'''
Created on Dec 3, 2012

@author: Steven
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

from fort.luminosity import luminosity

class LuminosityFunction(object):
    def __init__(self):
        pass

    def _KCorrect(self, gr_colour):
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

        kcor = np.zeros_like(np.array(self.survey_data["redshift"]))
        for x, a in enumerate(coeff):
            for y, b in enumerate(coeff[x]):
                kcor += coeff_A3[x][y] * self.survey_data["redshift"] ** x * gr_colour ** y

        return kcor


    def _LumDistance(self, c_dist):
        """
        Calculates the luminosity distance d_L according to d_L = (1+z)*c_dist
        where z is the redshift and c_dist is the line-of-sight comoving distance.
        Note that, in general, d_L = (1+z)*D_M, where D_M is the transverse comoving distance.
        For a "flat" cosmology (such as we are assuming here), D_M = c_dist
        """

        lum_dist = c_dist * (1 + self.survey_data["redshift"])
        return lum_dist

    def _AbsoluteMag(self, lum_dist, kcor=None):
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
            absmag = self.survey_data["mag_r"] - 5 * np.log10(lum_dist) - 25 - kcor
        else:
            absmag = self.survey_data["mag_r"] - 5 * np.log10(lum_dist) - 25

        return absmag

    def _LuminosityFromAbsMag(self, absmag):
        """
        Calculates the luminosity (actually, the base 10 log of the luminosity) using apparent magnitudes
        
        Note that the absolute magnitude of the sun is 4.83.
        WARNING:  Need to make sure that we are using abs. mag. for sun in r-band!
        """

        lum = np.log10(3.839 * 10 ** 26) + ((4.83 - absmag) / 2.512)

        return lum

    def EEP(self, Np=100, maxiter=5):
        """
        Calculates the Luminosity Function using the method of EEP
        
        Np - Number of bins in the luminosity function
        """
        kcor = self._KCorrect(self.survey_data['mag_g'] - self.survey_data['mag_r'])
        lumdist = self._LumDistance(self.survey_data["c_dist"])
        magr = np.asfortranarray(self.survey_data['mag_r'])
        phi, bins = luminosity.lumfunc(Np,
                                 absmag=np.asfortranarray(self.survey_data['absmag']),
                                 kcorr=np.asfortranarray(kcor),
                                 lumdist=np.asfortranarray(lumdist),
                                 magr=magr, maxiter=maxiter)


        plt.plot(bins, phi)
        plt.savefig(self._dirs['LuminosityFunction'] + 'EEP.pdf')
        plt.clf()
        return phi


