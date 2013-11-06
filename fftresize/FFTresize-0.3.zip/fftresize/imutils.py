#!/usr/bin/env python2

'''Read and write image files as NumPy arrays
'''


from matplotlib import image, pyplot
from numpy import amax, amin, around, uint8, zeros as _zeros
from os.path import exists, splitext
from random import randint
from sys import float_info as _float_info


def channels(img):
    '''The number of 2D channels in a 3D array.
    '''
    _channels = lambda x, y, z=1: z
    return _channels(*img.shape)


def _normalize(array):
    '''Normalize an array to the interval [0,1].
    '''
    min = amin(array)
    max = amax(array)
    array -= min
    array /= max - min
    eps = 10.0 * _float_info.epsilon
    negs = array < 0.0 + eps
    array[negs] = 0.0
    bigs = array > 1.0 - eps
    array[bigs] = 1.0
    return


def read(file):
    '''Return an array representing an image file.
    '''
    return image.imread(file)


def save(img, file):
    '''Save an array as a unique image file and return its path.
    '''
    while True:
        newfile = splitext(file)[0] + '-'
        newfile = newfile + str(randint(0, 1000)) + '.png'
        if not exists(newfile):
            break
    _normalize(img)
    uint8img = _zeros(img.shape, dtype=uint8)
    around(img * 255, out=uint8img)
    if channels(img) == 1:
        cmap = pyplot.cm.gray
    else:
        cmap = None
    pyplot.imsave(newfile, uint8img, cmap=cmap)
    return newfile


if __name__ == '__main__':
    pass
