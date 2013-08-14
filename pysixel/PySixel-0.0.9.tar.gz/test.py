#!/usr/bin/env python

import stbi
result = stbi.load("test.jpg")
print "x", result.x
print "y", result.y
print "n", result.n
print "len(data)", len(result.data)
print "len(palette)", len(result.palette)
result = None


