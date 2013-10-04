#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Image
import math
import sys


# The 256-color palette includes a 6x6x6 RGB color cube, with blue
# least-significant, starting at index 16

img = Image.open("../img/doge50x50.png")


# undo standard gamma correction to return a linear intensity
def invgamma(value):
    return math.pow(value, 2.2)


# redo gamma correction of intensity, returning image value
def gamma(intensity):
    return math.pow(intensity, 1.0/2.2)


# YUV color space
def toyuv(r, g, b):
    return (
        (0.299*r + 0.587*g + 0.114*b),
        (-0.14713*r - 0.28886*g + 0.436*b),
        (0.615*r - 0.51499*g - 0.10001*b))


# CIE XYZ color space
def toxyz(r, g, b):
    return (
        (0.49*r + 0.31*g + 0.20*b),
        (0.17697*r + 0.81240*g + 0.01063*b),
        (0.01*g + 0.99*b))


palette = []
for idx in range(6*6*6):
    ri = idx/36
    gi = (idx/6) % 6
    bi = idx % 6
    rf = invgamma(ri/5.0)
    gf = invgamma(gi/5.0)
    bf = invgamma(bi/5.0)
    palette.append(toxyz(rf, gf, bf))

# print palette


# these are r,g,b intensities, not color values (i.e. gamma corrected)
def bestcolor(r, g, b, alpha, dither):
    r = invgamma(max(0, float(r*alpha) / (255*255) - dither/12))
    g = invgamma(max(0, float(g*alpha) / (255*255) - dither/12))
    b = invgamma(max(0, float(b*alpha) / (255*255) - dither/12))
    xyz = toxyz(r, g, b)
    best, bestdist = None, 1e30
    for i in range(216):
        dist = ((palette[i][0] - xyz[0])**2 +
                (palette[i][1] - xyz[1])**2 +
                (palette[i][2] - xyz[2])**2)
        if dist < bestdist:
            bestdist = dist
            best = i + 16
    return best


bayer = [[1, 9, 3, 11],
         [13, 5, 15, 7],
         [4, 12, 2, 10],
         [16, 8, 14, 6]]

darken = float(sys.argv[1])
ditheramt = float(sys.argv[2])
for y in range(0, 50, 2):
    line = []
    for x in range(50):
        r1, g1, b1, a1 = img.getpixel((x, y))
        r2, g2, b2, a2 = img.getpixel((x, y+1))
        # multiply through by alpha
        f1 = darken + ditheramt * float(bayer[y % 4][x % 4]) / 17
        f2 = darken + ditheramt * float(bayer[(y+1) % 4][x % 4]) / 17
        topcolor = bestcolor(r1, g1, b1, a1, f1)
        bottomcolor = bestcolor(r2, g2, b2, a2, f2)
        if bottomcolor != topcolor:
            line.append("\033[38;5;%d;48;5;%dm▄" % (bottomcolor, topcolor))
        else:
            line.append("\033[48;5;%dm " % bottomcolor)
        # print x, y, "[", f1, r1, g1, b1, topcolor, "],
        # [", f2, r2, g2, b2, bottomcolor, "]"
    line.append("\033[0m")
    print(''.join(line))
