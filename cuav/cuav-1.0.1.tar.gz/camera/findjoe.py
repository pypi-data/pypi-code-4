#!/usr/bin/env python

import sys, cv, numpy

from optparse import OptionParser
parser = OptionParser("findjoe.py [options] <filename>")

parser.add_option("--lens",dest="lens", type='float', default='2.8',
                  help="lens size in mm")
parser.add_option("--illumination",dest="illumination", type='float', default='1500',
                  help="sunlight brightness in W/m^2")
parser.add_option("--lampdiameter",dest="lampdiameter", type='float', default='6.5',
                  help="lamp diameter in cm")
parser.add_option("--lampefficiency",dest="lampefficiency", type='float', default='10',
                  help="lamp efficieny (percentage)")
parser.add_option("--lamppower",dest="lamppower", type='float', default='50',
                  help="lamp power in W")
parser.add_option("--albedo",dest="albedo", type='float', default='0.2',
                  help="albedo of ground")
parser.add_option("--height", dest='height', type='float', default='122',
                  help='height in meters')
parser.add_option("--sensorwidth", dest='sensorwidth', type='float', default='5.0',
                  help='sensor width in mm')
parser.add_option("--filterfactor", dest='filterfactor', type='float', default='1.0',
                  help='filter pass ratio')
parser.add_option("--xresolution", dest='xresolution', type='int', default='1280')
    
(opts, args) = parser.parse_args()

if len(args) < 1:
    print("please supply an image file name")
    sys.exit(1)

def LoadPGM(filename):
    '''load a 16 bit PGM image'''
    f = open(filename, mode='r')
    fmt = f.readline()
    if fmt.strip() != 'P5':
        print('Expected P5 image in %s' % filename)
        return None
    dims = f.readline()
    if dims.strip() != '1280 960':
        print('Expected 1280x960 image in %s' % filename)
        return None
    line = f.readline()
    if line[0] == '#':
        line = f.readline()
    if line.strip() != '65535':
        print('Expected 16 bit image image in %s - got %s' % (filename, line.strip()))
        return None
    ofs = f.tell()
    f.close()
    a = numpy.memmap(filename, dtype='uint16', mode='c', order='C', shape=(960,1280), offset=ofs)
    a2 = a.byteswap(True)
    img = cv.CreateImageHeader((1280, 960), 16, 1)
    cv.SetData(img, a2.tostring(), a2.dtype.itemsize*1*1280)
    return img


def set_threshold(v):
    '''set the threshold to v'''
    global pgm
    timg = cv.CloneImage(pgm)
    for x in range(0, 1280):
        for y in range(0, 960):
            if timg[y, x] < v:
                timg[y,x] = 0
    cv.ShowImage(filename, timg)

filename = args[0]
pgm = LoadPGM(filename)
img = cv.LoadImage(filename, iscolor=False)

cv.NamedWindow(filename)
cv.CreateTrackbar('Threshold', filename, 0, 65535, set_threshold)
cv.ShowImage(filename, pgm)

cv.WaitKey()
