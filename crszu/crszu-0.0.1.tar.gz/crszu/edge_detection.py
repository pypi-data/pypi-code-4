#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PIL import Image


def find_edges(im):
    """
    Perform edge detection then find the edges.
    """
    result = []
    data = im.load()
    histx = [0 for x in range(im.size[0])]
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if data[x, y] == 1:
                histx[x] += 1

    for i in range(im.size[0]):
        if histx[i] > 0 and histx[i-1] <= 0:
            tmpx = i
        if histx[i] > 0 and histx[i+1] <= 0:
            histy = [0 for y in range(im.size[1])]
            for y in range(im.size[1]):
                for x in range(i+1)[tmpx:]:
                    if data[x, y] == 1:
                        histy[y] += 1
            for j in range(im.size[1]):
                if histy[j] > 0 and histy[j-1] <= 0:
                    tmpy1 = j
                    break
            for j in range(im.size[1])[::-1]:
                if histy[j] > 0 and histy[j+1] <= 0:
                    tmpy2 = j+1
                    break
            if i+1 - tmpx > 2 and tmpy2 - tmpy1 > 2:
                result.append((tmpx, tmpy1, i+1, tmpy2))
    return result
