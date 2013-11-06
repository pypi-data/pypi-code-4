#!/usr/bin/env python2

from numpy import amax, amin
from os.path import exists, splitext
from random import randint
from sys import float_info as _float_info


_channels = lambda x, y, z=1: z


def n_channels(array):
    return _channels(*array.shape)


def normalize(array):
    min = amin(array)
    max = amax(array)
    array -= min
    eps = 10.0 * _float_info.epsilon
    if (max - min) > eps:
        array /= (max - min)
    return


def rand_filename(file, ext=None):
    file_name, file_ext = splitext(file)
    if ext is None:
        ext = file_ext
    while True:
        rand_file_name = file_name
        rand_file_name += '-'
        rand_file_name += str(randint(0, 10000))
        rand_file_name += ext
        if not exists(rand_file_name):
            break
    return rand_file_name


if __name__ == '__main__':
    pass
