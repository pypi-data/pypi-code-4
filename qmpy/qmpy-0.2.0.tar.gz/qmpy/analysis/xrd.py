#!/usr/env/bin python

import itertools
import numpy as np
from qmpy.utils.math import *

def compute_d(cell, hkl):
    '''
    Takes a 1x6 array of lattice parameters, or a 3x3 array of lattice vectors,
    in combination with a 3x1 array of h, k, l indices and computes the
    interplanar distance of for that hkl vector.

    Example:
    >>> compute_d([3,4,5, 90, 90, 90], [1, 2, 3])

    '''
    cell = np.array(cell)
    if cell.shape == (6,):
        a, b, c, al, be, ga = cell
    elif cell.shape == (3,3):
        a, b, c, al, be, ga = basis_to_latparams(cell)
    a, b, c, al, be, ga = map(float, [a,b,c,al,be,ga])
    h, k, l = hkl
    d = 0
    d += h**2/(a**2*np.sin(al)**2)
    d += 2*k*l*(np.cos(be)*np.cos(ga)-np.cos(al))/(b*c)
    d += k**2/(b**2*np.sin(be)**2)
    d += 2*h*l*(np.cos(al)*np.cos(ga)-np.cos(be))/(a*c)
    d += l**2/(c**2*np.sin(ga)**2)
    d += 2*h*k*(np.cos(al)*np.cos(be)-np.cos(ga))/(a*b)
    d /= (1-np.cos(al)**2 - np.cos(be)**2 - np.cos(ga)**2 +
             2*np.cos(al)*np.cos(be)*np.cos(ga))
    return (1/d)**0.5

def compute_2theta(cell, hkl, wavelength=1.5418):
    '''
    Compute 2*theta for a given cell, in an hkl direction, for a given
    wavelength.
    '''
    d = compute_d(cell, hkl)
    return np.arcsin(wavelength/(2*d))*180/np.pi

def get_all_peaks(cell, min_2t=10, max_2t=70, wavelength=1.5418):
    '''
    For the given cell, it loops over hkl vectors within a range of 2theta 
    values, for a given wavelength.
    '''
    cell = np.array(cell)
    max_d = wavelength/(2*np.sin(max_2t*np.pi/360))
    if cell.shape == (3,3):
        cell = basis_to_latparams(cell)
    im, jm, km = map(lambda x: int(np.ceil(max_d*x)), cell[:3])
    peaks = []
    for h in range(-im, im+1):
        for k in range(-jm, jm+1):
            for l in range(-km, km+1):
                if [h,k,l] == [0,0,0]:
                    continue
                peak = compute_2theta(cell, [h,k,l])
                if peak > max_2t or peak < min_2t:
                    continue
                if not np.isnan(peak):
                    peaks.append(peak)
    return np.array(peaks)
