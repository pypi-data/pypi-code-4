# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 14:47:24 2013

@author: kshmirko
"""

__all__=['getRayleigh', 'getRayleighProfile']

import numpy as np
   

def _getAirMolarMass(CO2=360):
    """
    calculates mean molar mass for ambient air with specific amount of CO2
    >> m_air = getAirMass(360)
    CO2 = CO2 concentration im ppm
    
    """
    return 15.0556*CO2/1.0e6+28.9595 #g mol-1
    
    
def _getAirRefrIdx300ppmC02(wl=0.532):
    """
    ret refractive index for air with 300 ppm of CO2
    getAirRefrIdx300ppmC02(wl=0.532)
    """
    return (8060.77+2480990/(132.274-wl**(-2))+17455.7/(39.32957-wl**(-2)))/1.0e8+1
    
    
def _getAirRefrIdx360ppmC02(wl=0.532):
    """
    ret refractive index for air with 300 ppm of CO2
    getAirRefrIdx300ppmC02(wl=0.532)
    """
    return (8060.51+2481070/(132.274-wl**(-2))+17456.3/(39.32957-wl**(-2)))/1.0e8+1
    
    
def _getAirRefrIdxArbC02(wl=0.532, CO2=300):
    """
    """
    return (1+0.54*((CO2*1e-6)-300e-6))*(_getAirRefrIdx300ppmC02(wl)-1)+1
    
def _getFN2(wl=0.532):
    """
    (6+3p)/(6-7p) for N2
    _getFN2(wl)
    """
    return 1.034+3.17*1.0e-4*wl**(-2)
    
def _getFO2(wl=0.532):
    """
    (6+3p)/(6-7p) for O2
    _getFO2(wl)
    """
    return 1.096+1.385*1.0e-3*wl**(-2)+1.448*1.0e-4*wl**(-4)
    
    
def _getFAir(wl=0.532, CO2=300):
    """
    (6+3p)/(6-7p) for Air with specific amount of CO2
    """
    return (78.084*_getFN2(wl)+20.946*_getFO2(wl)+0.934+CO2*1.15)/(78.084+20.946+0.934+CO2)


def _getSigmaRayleigh(wl=0.532, CO2=300, T=288.15):
    """
    """
    n = _getAirRefrIdxArbC02(wl, CO2)
    F = _getFAir(wl, CO2)
    Ns = 6.0221367e23*273.15/(22.4141*T)/1000.0
    wl=wl*1e-4
    return (24*np.pi**3*(n**2-1)**2*F)/(wl**4*Ns**2*(n**2+2)**2)

def _getGravity(lat=43.1, alt=30):
    """
    return gravity acceleration for the specific geographical point (lat, alt)
    lat in degrees
    alt in meters
    >> g = _getGravity(lat=43.1, alt=30)
    """
    cos2phi=np.cos(2*np.deg2rad(lat))
    g0 = 980.6160*(1-0.0026373*cos2phi+0.0000059*cos2phi**2)
    g = g0 - (3.085462e-4+2.27e-7*cos2phi)*alt+\
        (7.254e-11+1.0e-13*cos2phi)*alt**2 -\
        (1.517e-17+6e-20*cos2phi)*alt**3
    return g
        
def _getMassWeightedAltitude(alt=30):
    """
    calculates mass-weighted altitude for optical thickness calculations
    """
    return 5517.56+0.73737*alt

def getRayleigh(wl=0.532, P=101300.0, CO2=300, lat=43.1, alt=30.0):
    """
    calculates rayleigh optical thickness
    >> tau_m = getRayleigh(wl=0.532, P=101300.0, T0=288.0, CO2=300, lat=43.1, alt=30.0)
    """
    T=288.15
    mwa = _getMassWeightedAltitude(alt)
    sigma = _getSigmaRayleigh(wl, CO2, T)
    mair = _getAirMolarMass(CO2)
    g = _getGravity(lat, mwa)
    A = 6.0221367e23
    tr = sigma*P*A*10/(mair*g) # Equation for t_r is: tr = sigma*P*A/(mair*g), 
                               # factor 10 is a conversion from Pa to dyn/cm2
    return tr

def getRayleighProfile(wl=0.532, P=None, CO2=300, lat=43.1, alt=None):
    """
    calculates Rayleigh scattering coefficient
    input P and alt are from upper air sounding data and could be unequally spaced
    
    for each P[i] and alt[i] calculates rayleigh tau and then - scattering coefficient
    """
    if isinstance(P, np.ndarray) and isinstance(alt, np.ndarray):
        Tau = np.array([getRayleigh(wl, P[i], CO2, lat, alt[i]) for i in np.arange(len(P))])
        alpha = -np.gradient(Tau)/np.gradient(alt)
        
    return alpha


    