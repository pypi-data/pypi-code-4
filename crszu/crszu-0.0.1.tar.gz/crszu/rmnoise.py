#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PIL import Image
from errors import InvalidSizeError, SizeTypeError


def rmnoise(im, size=5, min_nbs=2):
    """
    Remove noise pixels
    """
    data = im.load()
    width, height = im.size
    for x in range(width):
        for y in range(height):
            if data[x, y] == 255:
                continue
            else:
                nbs = count_neighbors(data, width, height, x, y, size)
                if nbs < min_nbs:
                    data[x, y] = 255
    return im


def count_neighbors(data, w, h, x, y, size=3):
    """
    Count number of black pixel in given neighbors.
    """
    nb = 0
    if not isinstance(size, int):
        raise SizeTypeError(size)
    if size < 0 or size == size / 2 * 2:
        raise InvalidSizeError(size)

    for i in range(x - ((size - 1) / 2), x + ((size - 1)) / 2):
        for j in range(y - ((size-1) / 2), y + ((size - 1)) / 2):
            if i < 0 or j < 0 or (x == i and y == j) or i >= w or j >= h:
                continue
            else:
                if data[i, j] == 1:
                    nb += 1
    return nb
