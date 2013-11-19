#!/usr/bin/env python2

'''FFTresize resizes images using zero-padding in the frequency
domain.
'''

from numpy import zeros as _zeros

from . import fftinterp
from . import imutils


__author__ = 'Mansour Moufid'
__copyright__ = 'Copyright 2013, Mansour Moufid'
__license__ = 'ISC'
__version__ = '0.4'
__email__ = 'mansourmoufid@gmail.com'
__status__ = 'Development'


def resize(filename, factor=1.5):
    '''Resize an image by zero-padding in the frequency domain.

    Return the filename of the resized image.
    '''
    img = imutils.read(filename)
    nchannels = imutils.channels(img)
    if nchannels == 1:
        new = fftinterp.interp2(img, factor)
    else:
        new = None
        for i in range(nchannels):
            rgb = img[:, :, i]
            newrgb = fftinterp.interp2(rgb, factor)
            if new is None:
                newsize = list(newrgb.shape)
                newsize.append(imutils.channels(img))
                new = _zeros(tuple(newsize))
            new[:, :, i] = newrgb
    return imutils.save(new, filename)


if '__main__' in __name__:
    pass
