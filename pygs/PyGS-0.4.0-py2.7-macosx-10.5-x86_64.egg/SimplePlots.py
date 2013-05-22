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

class SimplePlots(object):
    def __init__(self):
        return

    def PlotHist(self, quantity="redshift", bins=None, weight=None):
        """
        Plots a Histogram of the data for any quantity
        """

        if not bins:
            bins = utils.FD_bins(self.survey_data[quantity])


        plt.clf()
        plt.title("Histogram of " + quantity + " values for Sample " + self.sample_name + " from " + self.survey_name)
        if not weight:
            plt.hist(self.survey_data[quantity], bins)
        else:
            plt.hist(self.survey_data[quantity], bins, weights=self.survey_data[weight])

        plt.xlabel(quantity)
        plt.ylabel("Number")
        plt.savefig(self._dirs['SurveyPlots'] + 'Histogram_' + quantity + '_' + str(bins) + "bins.eps")
        plt.show()

    def PlotPolarDot(self, distance=False):
        """
        Makes a polar plot of the data, TODO: with an optional filter condition
            
        If distance is true, plots against comoving distance rather than redshift.
        """

        plt.clf()
        plt.title("Polar Plot of sample " + self.sample_name + " from " + self.survey_name)

        if not distance:
            plt.polar(self.survey_data['ra'], self.survey_data['redshift'], '.', markersize=1)
            plt.savefig(self._dirs['SurveyPlots'] + 'PolarPlot_Redshift.eps')
        else:
            plt.polar(self.survey_data['ra'], self.survey_data['c_dist'], '.', markersize=1)
            plt.savefig(self._dirs['SurveyPlots'] + 'PolarPlot_Distance.eps')
        plt.show()

    def PlotPolarSmooth(self, bins=None):
        """
        Makes a polar plot of the data smoothed by a filter., TODO: with an optional filter condition
            
        If distance is true, plots against comoving distance rather than redshift.
        """
        x_p = self.survey_data['c_dist'] * np.cos(self.survey_data['ra'])
        y_p = self.survey_data['c_dist'] * np.sin(self.survey_data['ra'])

        if not bins:
            bins = np.ceil(np.sqrt(self.N / 10000))
            if bins < 30:
                bins = 30

        smooth = np.histogram2d(x_p, y_p, ((bins, bins)))[0]

        plt.clf()
        plt.title("Smoothed Polar Plot of sample " + self.sample_name + " from " + self.survey_name)
        plt.imshow(smooth, interpolation="Gaussian", aspect='equal')
        plt.tick_params(axis='both', labelbottom=False, labelleft=False)
        plt.savefig(self._dirs['SurveyPlots'] + 'PolarPlot_Smooth.eps')
        plt.show()

    def PlotSkyDot(self):
        """
        Makes a 2-D flat sky-plot of the data points.
        """

        plt.clf()
        plt.title("Sky Plot of sample " + self.sample_name + " from " + self.survey_name)
        plt.plot(self.survey_data['ra'], self.survey_data['dec'], '.', markersize=1)
        plt.xlabel("Right Ascension")
        plt.ylabel("Declination")
        plt.savefig(self._dirs['SurveyPlots'] + 'SkyPlot.eps')
        plt.show()

    def PlotSkySmooth(self, bins=None):
        """
        Makes a 2-D flat sky-plot of the data points, smoothed by Gaussian filter.
        """
        plt.clf()
        plt.title("Smoothed Sky Plot of sample " + self.sample_name + " from " + self.survey_name)

        if not bins:
            bins = np.ceil(np.sqrt(self.N / 10000))
            if bins < 30:
                bins = 30

        smooth = np.histogram2d(self.survey_data['ra'], self.survey_data['dec'], ((bins, bins)))[0]

        plt.clf()
        plt.imshow(smooth, interpolation=None, aspect='equal', extent=(np.min(self.survey_data['ra']),
                    np.max(self.survey_data['ra']), np.min(self.survey_data['dec']), np.max(self.survey_data['dec'])))
        plt.tick_params(axis='both')
        plt.savefig(self._dirs['SurveyPlots'] + 'SkyPlot_Smooth.eps')
        plt.show()
