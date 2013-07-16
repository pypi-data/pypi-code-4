#!/bin/env python

import sys
import pygame
import pgext
import time

pygame.display.init()
pygame.display.set_mode((1, 1))



class Tester:
    def __init__(self, source_image, num=1):
        self.num = num
        self.source = pygame.image.load(source_image)
        self.tests = {}
        self.order = []
        self.results = {}
        self.result_surfaces = {}
        self.times_start = {}
        self.times_result = {}
        self.types = ["mrt", "mip", "make"]

    def addTests(self, tests):
        for t in tests:
            self.addTest(t)

    def addTest(self, test):
        source = self.source

        if len(test) == 4:
            name, typ, func, args = test
        else:
            name, typ, func, args, source = test

        if not typ in self.types:
            print "Unknown test type: %s" % typ
            return False
        self.tests[name] = (typ, func, args, source)
        self.order.append(name)
        self.times_result[name] = []
        return True

    def saveImage(self, name, image):
        self.result_surfaces[name] = image

    def saveAll(self):
        for name in self.result_surfaces:
            image = self.result_surfaces[name]
            pygame.image.save(image, "out_%s.png" % name)

    def meterStart(self, name):
        self.times_start[name] = time.time()

    def meterEnd(self, name):
        self.times_result[name].append((time.time() -
                                       self.times_start[name]) * 1000)

    def doTests(self, single=None):
        for n in xrange(self.num):
            for test in self.order:
                if single and test not in single:
                    continue
                self.doTest(test, n)
        self.saveAll()

    def doTest(self, name, n=1):
        print "%sTest: %s/%s %s" % (("\b" * 80), n + 1, self.num,  name),
        try:
            test = self.tests[name]
            source = test[3].copy()
            if test[0] == "mrt":
                self.meterStart(name)
                image = test[1](source, *test[2])
                self.meterEnd(name)
                self.saveImage(name, image)
            elif test[0] == "mip":
                self.meterStart(name)
                test[1](source, *test[2])
                self.meterEnd(name)
                self.saveImage(name, source)
            elif test[0] == "make":
                self.meterStart(name)
                image = test[1](*test[2])
                self.meterEnd(name)
                self.saveImage(name, image)

            self.results[name] = 0
        except Exception, e:
            self.results[name] = e

    def printResults(self):
        print "%sTesting cycles: %s" % (("\b" * 80), self.num)
        count = 0
        for test in self.order:
            if not test in self.results:
                continue
            t = self.times_result[test]
            if self.results[test]:
                print "%s: Error (%s)" % (test, t)
            else:
                avgtime = sum(t) / float(len(t))
                count += avgtime
                print "%21s: %.1f ms" % (test, avgtime)
        print "%21s: %.1f ms" % ("Total time", count)

source_rgb = pygame.image.load("source_rgb.png").convert()
source_rgba = pygame.image.load("source_rgba.png")
source_mask = pygame.image.load("source_mask.png")
source_mask2 = pygame.image.load("source_mask2.png")

tester = Tester("source_rgb.png", 1)

tester.addTests([
    ("color.colorize", "mip", pgext.color.colorize, [0, 200, -30, 10]),
    ("color.greyscale1", "mip", pgext.color.greyscale, []),
    ("color.greyscale2", "mip", pgext.color.greyscale, [1]),
    ("color.greyscale3", "mip", pgext.color.greyscale, [2]),
    ("color.invert", "mip", pgext.color.invert, []),
    ("color.contrast1", "mip", pgext.color.contrast, [80]),
    ("color.contrast2", "mip", pgext.color.contrast, [-80]),
    ("color.brightness1", "mip", pgext.color.brightness, [80]),
    ("color.brightness2", "mip", pgext.color.brightness, [-80]),
    ("color.hue", "mip", pgext.color.hue, [80]),
    ("color.saturation", "mip", pgext.color.saturation, [30, 2]),
    ("color.lightness", "mip", pgext.color.lightness, [20]),
    ("color.value", "mip", pgext.color.value, [-50]),
    ("color.multiply1", "mip", pgext.color.multiply, [2.5]),
    ("color.multiply2", "mip", pgext.color.multiply, [0.4]),
    ("color.multiply3", "mip", pgext.color.multiply, [0.0, 1, 0, 1]),
    ("color.setColor", "mip", pgext.color.setColor, [(120, 0, 200)], source_rgba),
    ("color.setAlpha", "mip", pgext.color.setAlpha, [40, 2], source_rgba),
    ("color.alphaMask", "mrt", pgext.color.alphaMask, [source_mask], source_rgb),
    ("color.alphaMask2", "mrt", pgext.color.alphaMask, [source_mask2, 1], source_rgb),

    ("filters.shadow", "mrt", pgext.filters.shadow, [(0, 0, 0), 5, 1, 0.9], source_rgba),
    ("filters.shadow2", "mrt", pgext.filters.shadow, [(200, 0, 0), 10, 0, 0.9], source_rgba),
    ("filters.blur", "mip", pgext.filters.blur, [4]),
    ("filters.hvBlur-h", "mip", pgext.filters.hvBlur, [6, 0]),
    ("filters.hvBlur-v", "mip", pgext.filters.hvBlur, [6, 1]),

    ("filters.noise", "mip", pgext.filters.noise, [55, 2]),
    ("filters.noiseBlur1", "mip", pgext.filters.noiseBlur, [5]),
    ("filters.noiseBlur2", "mip", pgext.filters.noiseBlur, [20, 1]),
    ("filters.scratch", "mip", pgext.filters.scratch, [5]),
    ("filters.pixelize", "mip", pgext.filters.pixelize, [10]),

    ("filters.ripple", "mip", pgext.filters.ripple, [30, 4]),

    ("filters.gradient1", "make", pgext.filters.gradient, [(200, 200), (100, 100, 200), (100, 200, 100), 0, 1.0]),
    ("filters.gradient2", "make", pgext.filters.gradient, [(200, 200), (255, 0, 0, 0), (0, 0, 255, 255), 0, 0.3]),
    ("filters.gradient3", "make", pgext.filters.gradient, [(200, 200), (100, 0, 0), (0, 55, 55), 1, 1.0]),

])

try:
    tests = sys.argv[1:]
except:
    tests = None

tester.doTests(tests)
tester.printResults()
