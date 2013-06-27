# -*- coding: utf-8 -*-
#!/usr/bin/python
# Cross Wavelet Analysis (CWA) based on Maraun and Kurths(2004).
# http://www.nonlin-processes-geophys.net/11/505/2004/npg-11-505-2004.pdf
# author: Mabel Calim Costa
# INPE
# 23/01/2013

"""
Created on Mon Jun 17 2013

@author: Mabel Calim Costa
"""



def cross_wavelet (wave1,wave2):
    """ Computes the cross wavelet analysis.
        A normalized time and scale resolved measure for the relationship 
        between two time series x1(ti) and x2(ti) is the wavelet coherency (WCO),
        which is defined as the amplitude of the WCS(wavelet cross spectrum) 
        normalized to the two single WPS(wavelet power spectrum) (Maraun and Kurths,2004).
         	WCOi(s) = |WCSi(s) |/ (WPSi1(s) WPSi2(s)) ˆ1/2 
        _____________________________________________________________________
        Inputs:  
		wave1 - wavelet transform of time series x1
                wave2 - wavelet transform of time series x2
        Outputs:
		cohere - wavelet coherency (WCO)
 	Call function:
		cohere = cross_wavelet(wave1,wave2)
    """ 
    cross_power = np.abs(wave1.real*wave2.imag)
    cohere = cross_power/np.sqrt(np.abs(wave1*wave1)* np.abs(wave2*wave2))
    return cohere

