#!/bin/env python

import sys
import pygame
from pgext import color, filters
import time

INPLACE = 1
RETURNCOPY = 2

source_rgb = pygame.image.load("source_rgb.png")
source_rgba = pygame.image.load("source_rgba.png")
source_mask = pygame.image.load("source_mask.png")
source_mask2 = pygame.image.load("source_mask2.png")

TESTS = {
    "color.alphaMask": (RETURNCOPY, color.alphaMask, (source_rgb, source_mask)),
    "color.alphaMask2": (RETURNCOPY, color.alphaMask, (source_rgb, source_mask2, 1)),
    "color.brightness1": (INPLACE, color.brightness, (source_rgb, 80)),
    "color.brightness2": (INPLACE, color.brightness, (source_rgb, -80)),
    "color.colorize": (INPLACE, color.colorize, (source_rgb, 0, 200, -30, 10)),
    "color.contrast1": (INPLACE, color.contrast, (source_rgb, 80)),
    "color.contrast2": (INPLACE, color.contrast, (source_rgb, -80)),
    "color.desaturate": (INPLACE, color.desaturate, (source_rgb, 0.5)),
    "color.greyscale1": (INPLACE, color.greyscale, (source_rgb, )),
    "color.greyscale2": (INPLACE, color.greyscale, (source_rgb, 1)),
    "color.greyscale3": (INPLACE, color.greyscale, (source_rgb, 2)),
    "color.hue": (INPLACE, color.hue, (source_rgb, 80)),
    "color.invert": (INPLACE, color.invert, (source_rgb, )),
    "color.lightness": (INPLACE, color.lightness, (source_rgb, 20)),
    "color.multiply1": (INPLACE, color.multiply, (source_rgb, 2.5)),
    "color.multiply2": (INPLACE, color.multiply, (source_rgb, 0.4)),
    "color.multiply3": (INPLACE, color.multiply, (source_rgb, 0.0, 1, 0, 1)),
    "color.saturation": (INPLACE, color.saturation, (source_rgb, 30, 2)),
    "color.setAlpha": (INPLACE, color.setAlpha, (source_rgb, 40, 2), source_rgba),
    "color.setColor": (INPLACE, color.setColor, (source_rgba, (120, 0, 200))),
    "color.setColor2": (INPLACE, color.setColor, (source_rgba, (120, 0, 200, 80))),
    "color.value": (INPLACE, color.value, (source_rgb, -50)),
    "filters.blur": (INPLACE, filters.blur, (source_rgb, 4)),
    "filters.gradient1": (RETURNCOPY, filters.gradient, ((200, 200), (100, 100, 200), (100, 200, 100), 0, 1.0)),
    "filters.gradient2": (RETURNCOPY, filters.gradient, ((200, 200), (255, 0, 0, 0), (0, 0, 255, 255), 0, 0.3)),
    "filters.gradient3": (RETURNCOPY, filters.gradient, ((200, 200), (100, 0, 0), (0, 55, 55), 1, 1.0)),
    "filters.hvBlur-h": (INPLACE, filters.hvBlur, (source_rgb, 6, 0)),
    "filters.hvBlur-v": (INPLACE, filters.hvBlur, (source_rgb, 6, 1)),
    "filters.noise": (INPLACE, filters.noise, (source_rgb, 55, 2)),
    "filters.noiseBlur1": (INPLACE, filters.noiseBlur, (source_rgb, 5)),
    "filters.noiseBlur2": (INPLACE, filters.noiseBlur, (source_rgb, 20, 1)),
    "filters.pixelize": (INPLACE, filters.pixelize, (source_rgb, 10)),
    "filters.ripple": (INPLACE, filters.ripple, (source_rgb, 30, 4)),
    "filters.scratch": (INPLACE, filters.scratch, (source_rgb, 5)),
    "filters.shadow": (RETURNCOPY, filters.shadow, (source_rgba, (0, 0, 0), 5, 1, 0.9)),
    "filters.shadow2": (RETURNCOPY, filters.shadow, (source_rgba, (200, 0, 0), 10, 0, 0.9)),
}


def run_test(test_key):
    t = TESTS[test_key]
    if t[0] == INPLACE:
        try:
            length = time.time()
            args = list(t[2])
            args[0] = args[0].copy()
            t[1](*args)
            length = (time.time() - length) * 1000
            print "OK: %s %.1f ms" % (test_key, length)
            pygame.image.save(args[0], "results/%s.png" % test_key)
            return length
        except Exception, e:
            print "FAILED: %s %s" % (test_key, e)
            return 0
    elif t[0] == RETURNCOPY:
        try:
            length = time.time()
            result = t[1](*t[2])
            length = (time.time() - length) * 1000
            print "OK: %s %.1f ms" % (test_key, length)
            pygame.image.save(result, "results/%s.png" % test_key)
            return length
        except Exception, e:
            print "FAILED: %s %s" % (test_key, e)
            return 0

try:
    # run single test
    tst = sys.argv[1]
    run_test(tst)
except:
    # run all tests
    tkeys = TESTS.keys()
    tkeys.sort()
    length = 0
    for k in tkeys:
        length += run_test(k)
    print "Time: %.2f ms" % length
