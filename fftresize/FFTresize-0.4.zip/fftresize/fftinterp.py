#!/usr/bin/env python2

'''2D interpolation using zero-padding in the frequency domain
'''


from numpy import complex64, real, zeros as _zeros
from numpy.fft import fft2, ifft2, fftshift, ifftshift


def _zeropad2(x, shape):
    '''Pad a two-dimensional NumPy array with zeros along its borders
    to the specified shape.
    '''
    m, n = x.shape
    p, q = shape
    assert p > m
    assert q > n
    tb = (p - m) / 2
    lr = (q - n) / 2
    xpadded = _zeros(shape, dtype=complex64)
    xpadded[tb:tb + m, lr:lr + n] = x
    return xpadded


def interp2(array, factor):
    '''Interpolate a two-dimensional NumPy array by a given factor.
    '''
    reshape = lambda (x, y): [int(factor * x), int(factor * y)]
    diff = lambda (x, y): [x - array.shape[0], y - array.shape[1]]
    nexteven = lambda x: x if (x % 2 == 0) else x + 1
    delta = map(nexteven, diff(reshape(array.shape)))
    newsize = tuple(x[0] + x[1] for x in zip(array.shape, delta))
    fft = fft2(array)
    fft = fftshift(fft)
    fft = _zeropad2(fft, newsize)
    ifft = ifftshift(fft)
    ifft = ifft2(ifft)
    ifft = real(ifft)
    return ifft


if '__main__' in __name__:
    pass
