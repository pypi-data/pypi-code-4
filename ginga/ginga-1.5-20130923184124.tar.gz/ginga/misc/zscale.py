# Copyright (c) 2005, 2006, 2007, Jeremy Brewer
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are 
# met:
# 
#     * Redistributions of source code must retain the above copyright 
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in 
#       the documentation and/or other materials provided with the
#       distribution.
#     * The names of the contributors may not be used to endorse or 
#       promote products derived from this software without specific prior 
#       written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT 
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy
import math
import scipy.optimize as optimize

def calc_range(data, contrast=None, num_points=None, num_per_row=None):

    """
    Computes the range of pixel values to use when adjusting the contrast
    of FITs images using the zscale algorithm.  The zscale algorithm
    originates in Iraf.  More information about it can be found in the help
    section for DISPLAY in Iraf.

    Briefly, the zscale algorithm uses an evenly distributed subsample of the
    input image instead of a full histogram.  The subsample is sorted by
    intensity and then fitted with an iterative least squares fit algorithm.
    The endpoints of this fit give the range of pixel values to use when
    adjusting the contrast.

    Input:  data  -- the array of data contained in the FITs image
                           (must have 2 dimensions)
            contrast    -- the contrast parameter for the zscale algorithm
            num_points  -- the number of points to use when sampling the
                           image data
            num_per_row -- number of points per row when sampling
    
    Return: 1.) The minimum pixel value to use when adjusting contrast
            2.) The maximum pixel value to use when adjusting contrast
    """

    assert len(data.shape) >= 2, \
           ValueError("input data should be 2D or greater")
    ht, wd = data.shape[:2]

    if contrast == None:
        #contrast = 0.25
        contrast = 0.40
        
    assert (0.0 < contrast <= 1.0), \
           ValueError("contrast (%.2f) not in range 0 < c <= 1" % (
        contrast))
    
    total_points = numpy.size(data)
    if num_points == None:
        num_points = total_points * 0.0002
        
    assert (0 < num_points < total_points), \
           ValueError("num_points not in range 0-%d" % (total_points))

    if num_per_row == None:
        num_per_row = int(0.015 * num_points)
        
    # determine the number of points in each column
    num_per_col = int(num_points / num_per_row)

    # sample the array 
    xskip = int(float(wd-1) / num_per_col)
    yskip = int(float(ht-1) / num_per_row)

    cutout = data[0:ht-1:yskip, 0:wd-1:xskip]
    cutout = cutout.flat
    
    # actual number of points selected
    num_pix = len(cutout)
    # assert num_pix <= num_points, \
    #        ValueError("Actual number of points (%d) exceeds calculated number (%d)" % (
    #     num_pix, num_points))
    
    # sort the data by value
    cutout = numpy.sort(cutout)

    # check for a flat distribution of pixels
    data_min = numpy.nanmin(cutout)
    data_max = numpy.nanmax(cutout)
    if data_min == data_max:
        return data_min, data_max

    # compute the median
    cx = (num_pix // 2)
    if num_pix % 2 != 0:
        median = cutout[cx]
    else:
        median = 0.5 * (cutout[cx-1] + cutout[cx])

    # compute an iterative fit to intensity
    # TODO: replace with scipy LSF
    pixel_indeces = map(float, xrange(num_pix))
    points = PointArray(pixel_indeces, list(cutout), min_err=1.0e-4)
    fit = points.sigmaIterate()

    ## def fitting(x, p):
    ##     """zscale fitting function.
    ##     I(i) = intercept + slope * (i - midpoint)

    ##     p[0]==mean, p[1]==sdev, p[2]=maxv
    ##     """
    ##     y = (1.0 / (p[1] * numpy.sqrt(2*numpy.pi)) *
    ##          numpy.exp(-(x - p[0])**2 / (2*p[1]**2))) * p[2]
    ##     return y

    ## X = numpy.array(range(num_pix))
    ## Y = numpy.array(cutout)

    ## errfunc = lambda p, x, y: gauss_fn(x, p) - y
    ## # Least square fit to the gaussian
    ## #with self.lock:
    ## # NOTE: without this mutex, optimize.leastsq causes a fatal error
    ## # sometimes--it appears not to be thread safe.
    ## # The error is:
    ## # "SystemError: null argument to internal routine"
    ## # "Fatal Python error: GC object already tracked"
    ## p1, success = optimize.leastsq(errfunc, p0[:], args=(X, Y))

    # if not success:
    #     raise IQCalcError("gaussian fitting failed")

    num_allowed = 0
    for pt in points.allowedPoints():
        num_allowed += 1

    if num_allowed < int(num_pix / 2.0):
        return data_min, data_max

    # compute the limits
    z1 = median - cx * (fit.slope / contrast)
    z2 = median + (num_pix - cx) * (fit.slope / contrast)

    zmin = max(z1, data_min)
    zmax = min(z2, data_max)

    # last ditch sanity check
    if zmin >= zmax:
        zmin = data_min
        zmax = data_max

    return zmin, zmax


def calc_range3(image_data, contrast=0.25, num_points=600, num_per_row=120):

    """
    Computes the range of pixel values to use when adjusting the contrast
    of FITs images using the zscale algorithm.  The zscale algorithm
    originates in Iraf.  More information about it can be found in the help
    section for DISPLAY in Iraf.

    Briefly, the zscale algorithm uses an evenly distributed subsample of the
    input image instead of a full histogram.  The subsample is sorted by
    intensity and then fitted with an iterative least squares fit algorithm.
    The endpoints of this fit give the range of pixel values to use when
    adjusting the contrast.

    Input:  image_data  -- the array of data contained in the FITs image
                           (must have 2 dimensions)
            contrast    -- the contrast parameter for the zscale algorithm
            num_points  -- the number of points to use when sampling the
                           image data
            num_per_row -- number of points per row when sampling
    
    Return: 1.) The minimum pixel value to use when adjusting contrast
            2.) The maximum pixel value to use when adjusting contrast
    """

    # check input shape
    if len(image_data.shape) != 2:
        raise ValueError("input data is not an image")

    # check contrast
    if contrast <= 0.0:
        contrast = 1.0

    # check number of points to use is sane
    if num_points > numpy.size(image_data) or num_points < 0:
        num_points = 0.5 * numpy.size(image_data)

    # determine the number of points in each column
    num_per_col = int(float(num_points) / float(num_per_row) + 0.5)

    # integers that determine how to sample the control points
    xsize, ysize = image_data.shape
    row_skip = float(xsize - 1) / float(num_per_row - 1)
    col_skip = float(ysize - 1) / float(num_per_col - 1)

    # create a regular subsampled grid which includes the corners and edges,
    # indexing from 0 to xsize - 1, ysize - 1
    data = []
   
    for i in xrange(num_per_row):
        x = int(i * row_skip + 0.5)
        for j in xrange(num_per_col):
            y = int(j * col_skip + 0.5)
            data.append(image_data[x, y])

    # actual number of points selected
    num_pixels = len(data)

    # sort the data by intensity
    data.sort()

    # check for a flat distribution of pixels
    data_min = min(data)
    data_max = max(data)
    center_pixel = (num_pixels + 1) / 2
    
    if data_min == data_max:
        return data_min, data_max

    # compute the median
    if num_pixels % 2 == 0:
        median = data[center_pixel - 1]
    else:
        median = 0.5 * (data[center_pixel - 1] + data[center_pixel])

    # compute an iterative fit to intensity
    # TODO: replace with scipy LSF
    pixel_indeces = map(float, xrange(num_pixels))
    points = PointArray(pixel_indeces, data, min_err=1.0e-4)
    fit = points.sigmaIterate()

    num_allowed = 0
    for pt in points.allowedPoints():
        num_allowed += 1

    if num_allowed < int(num_pixels / 2.0):
        return data_min, data_max

    # compute the limits
    z1 = median - (center_pixel - 1) * (fit.slope / contrast)
    z2 = median + (num_pixels - center_pixel) * (fit.slope / contrast)

    if z1 > data_min:
        zmin = z1
    else:
        zmin = data_min

    if z2 < data_max:
        zmax = z2
    else:
        zmax = data_max

    # last ditch sanity check
    if zmin >= zmax:
        zmin = data_min
        zmax = data_max

    return zmin, zmax

# Class for performing least squares fits
# Copyright (c) 2005, 2006, 2007, Jeremy Brewer
# 
"""
The PointArray class is designed for iterative least squares fitting routines
where points must be rejected on each pass.  It makes it easy to perform
these fits and to report on which points were actually used in the fitting.

Example Usage:

num_points = 100
x = []
y = []
for i in xrange(num_points - 5):
    x.append(float(i))
    y.append(float(i + 1))

# create 5 bad points
x.append(15.2)
y.append(65.8)

x.append(56.7)
y.append(14.6)

x.append(23.5)
y.append(67.8)

x.append(12.1)
y.append(30.0)

x.append(4.0)
y.append(50.0)

# create a PointArray
p = pointarray.PointArray(x, y, min_err=1.0e-4)
print "Points:\n%s" % p

fit = p.sigmaIterate()
print "Iterative least squares fit: %s" % fit   
print "Rejected points:"
for pt in p.rejectedPoints():
    print pt
"""

def distance(point, line):
    
    """
    Returns the delta y offset distance between a given point (x, y) and a
    line evaluated at the x value of the point.
    """
    
    return point.y - line(point.x)
    
def perp_distance(point, line):
    
    """
    Returns the perpendicular offset distance between a given point (x, y)
    and a line evaluated at the x value of the point.
    """
    
    return (point.y - line(point.x)) / math.sqrt(1.0 + line.slope ** 2)

class Point(object):

    """Class for representing points"""
    
    def __init__(self, x, y, y_err=0.0):
        self.x = x
        self.y = y
        self.y_err = y_err
        self.isRejected = False

    def __str__(self):
        if self.isRejected:
            s = "(%f, %f +- %f) R" % (self.x, self.y, self.y_err)
        else:
            s = "(%f, %f +- %f)" % (self.x, self.y, self.y_err)
        return s

    def allow(self):
        self.isRejected = False

    def reject(self):
        self.isRejected = True

class PointArray(object):

    """Class for arrays of points"""
    
    def __init__(self, x, y, y_err=None, min_err=1.0e-14):

        # check args
        assert len(x) == len(y)
        assert min_err > 0.0

        if y_err:
            assert len(x) == len(y_err)

            # build a list of y errors that is filtered for the minimum err
            err = []
            for e in y_err:
                if e >= min_err:
                    err.append(e)
                else:
                    err.append(min_err)
        else:
            err = [min_err] * len(x)

        # create a list of points
        self.points = map(Point, x, y, err)

    def __str__(self):
        return "\n".join(map(str, self.points))

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        """Allows iteration in for statements"""
        for point in self.points:
            yield point

    def allowedPoints(self):
        """Allows iteration over only allowed points"""
        for pt in self.points:
            if not pt.isRejected:
                yield pt

    def rejectedPoints(self):
        """Allows iteration over only rejected points"""
        for pt in self.points:
            if pt.isRejected:
                yield pt

    def __getitem__(self, i):
        return self.points[i]

    def __setitem__(self, i, value):
        if not isinstance(value, Point):
            raise TypeError("object to set is not a Point")
        self.points[i] = value

    def allowAll(self):
    
        """
        Resets all points to be allowed.
        """

        for pt in self.rejectedPoints():
            pt.isRejected = False

    def leastSquaresFit(self):
        
        """
        Performs a least squares fit on the input data.
        """
        
        S = 0.0
        Sx = 0.0
        Sy = 0.0
        Sxy = 0.0
        Sxx = 0.0
        Syy = 0.0
        
        # compute sums
        for pt in self.allowedPoints():
            variance = pt.y_err ** 2
            S += 1.0 / variance
            Sx += pt.x / variance
            Sy += pt.y / variance
            Sxx += (pt.x ** 2) / variance
            Syy += (pt.y ** 2) / variance
            Sxy += (pt.x * pt.y) / variance

        # check for all points rejected
        if S == 0.0:
            return LinearFit()

        # compute the slope using a technique to minimize roundoff (see
        # Numerical Recipes for details)
        Stt = 0.0
        slope = 0.0

        for pt in self.allowedPoints():
            t = (pt.x - Sx / S) / pt.y_err
            Stt += t ** 2
            slope += (t * pt.y) / pt.y_err 

        slope /= Stt
        intercept = (Sy - Sx * slope) / S
        r2 = (Sxy * S - Sx * Sy) / \
             math.sqrt((S * Sxx - Sx * Sx) * (S * Syy - Sy * Sy))
              
        return LinearFit(slope, intercept, r2)

    def perpLeastSquaresFit(self):

        """
        Performs a perpendicular offset least squares fit on the input data.
        """

        S = 0.0
        Sx = 0.0
        Sy = 0.0
        Sxy = 0.0
        Sxx = 0.0
        Syy = 0.0
        
        # compute sums
        for pt in self.allowedPoints():
            variance = pt.y_err ** 2
            S += 1.0 / variance
            Sx += pt.x / variance
            Sy += pt.y / variance
            Sxx += (pt.x ** 2) / variance
            Syy += (pt.y ** 2) / variance
            Sxy += (pt.x * pt.y) / variance

        # check for all points rejected
        if S == 0.0:
            return LinearFit()

        B = ((S * Syy - Sy * Sy) - (S * Sxx - Sx * Sx)) / \
            (2.0 * (Sx * Sy - Sxy * S))

        # there are two solutions for the slope
        m = -B + math.sqrt(B * B + 1.0)
        m2 = -B - math.sqrt(B * B + 1.0)
        r2 = (Sxy * S - Sx * Sy) / \
                math.sqrt((S * Sxx - Sx * Sx) * (S * Syy - Sy * Sy))

        # slope for regular least squares fitting
        delta = S * Sxx - Sx * Sx
        ls_slope = (S * Sxy - Sx * Sy) / delta

        # choose the slope that is closest to normal least squares fitting
        diff = abs(ls_slope - m)
        diff2 = abs(ls_slope - m2)

        if diff <= diff2:
            slope = m
        else:
            slope = m2
            
        intercept = (Sy - slope * Sx) / S
        return LinearFit(slope, intercept, r2)

    def stddev(self, fit):
    
        """
        Returns the standard deviation of the difference from the input fit
        line for allowed points.  Returns -1 if there are too few allowed
        points to compute the standard deviation.
        """

        count = 0
        variance = 0.0

        for pt in self.allowedPoints():
            # take <y> as the value of the fit point at each point x
            delta = pt.y - fit(pt.x)
            variance += delta ** 2
            count += 1

        if count <= 1:
            return -1.0
        else:
            # the variance is bias corrected
            variance /= float(count - 1)
            sigma = math.sqrt(variance)
            return sigma

    def perpStddev(self, fit):

        """
        Returns the standard deviation of the perpendicular offset difference
        from the input fit line for allowed points.  Returns -1 if there are
        too few allowed points to compute the standard deviation.
        """

        count = 0
        variance = 0.0

        for pt in self.allowedPoints():
            # take <y> as the value of the fit point at each point x
            delta = (pt.y - fit(pt.x)) / math.sqrt(1.0 + fit.slope ** 2)
            variance += delta ** 2
            count += 1

        if count <= 1:
            return -1.0
        else:
            # the variance is bias corrected
            variance /= float(count - 1)
            sigma = math.sqrt(variance)
            return sigma

    def sigmaIterate(self, max_iter=5, max_sigma=3.0, perp_offset=False,
                     initial_fit=None):
        
        """
        Performs an iterative sigma clipping fit on the input data set.  A
        least squares line is fit to the data, then points further than
        max_sigma stddev away will be thrown out and the process repeated
        until no more points are rejected, all points are rejected, or the
        maximum number of iterations is passed.
        
        The sigma clipping algorithm uses either standard or perpendicular
        offset least squares fitting depending on the perp_offset flag.  By
        default normal least squares fitting is used.
        
        An optional initial fit to use can be supplied via initial_fit.  This
        is useful for noisy data where the "true" fit is approximately known
        beforehand.
        """

        # determine fit algorithm to use
        if perp_offset:
            lsFit = self.perpLeastSquaresFit
            stddev = self.perpStddev
            dist = perp_distance
        else:
            lsFit = self.leastSquaresFit
            stddev = self.stddev
            dist = distance
        
        # total number of rejected points
        total = 0
        
        for pt in self.points:
            if pt.isRejected:
                total += 1
        
        # initial fit
        if initial_fit is None:
            fit = lsFit()
        else:
            fit = initial_fit

        for i in xrange(max_iter):
            # standard deviation from fit line
            three_sigma = max_sigma * stddev(fit)
            
            # number of newly rejected points on each pass
            count = 0

            # throw away outliers
            for pt in self.allowedPoints():
                diff = abs(dist(pt, fit))
                if diff > three_sigma:
                    pt.isRejected = True
                    count += 1

            total += count

            # exit if none or all of the points were rejected
            if count == 0:
                break
            elif total == len(self.points):
                raise ValueError("all points were rejected")

            # update the fit
            fit = lsFit()

        return fit


"""
Line class module

The Line class is a simple class for holding the slope and intercept of a
line.  Line objects are callable -- when called, they evaluate at the given
x value, e.g. y = line(x) gives the value of line at x.

Example Usage.:

l = line.Line(2.0, 3.0)
x1, x2, x3 = 3.14, 0.0, 1.0

print "The line is %s" % l
print "f(%f) = %f" % (x1, l(x1))
print "f(%f) = %f" % (x2, l(x2))
print "f(%f) = %f" % (x3, l(x3))

lp = l.perpToAtX(0.0)
print "Line perpendicular to original at x = 0 is %s" % lp
lp = l.perpToAtY(3.0)
print "Line perpendicular to original at y = 3 is %s" % lp

flip = l.flipXY()
print "Line with flipped x, y is %s" % flip

fit = line.LinearFit(2.0, 3.0, 0.987)
print "Linear fit is %s" % fit
"""

class Line(object):

    """Class for describing lines"""

    def __init__(self, slope=0.0, intercept=0.0):

        """
        Initializes a line to have the given slope and intercept.
        
        Input:  slope     -- slope of the line
                intercept -- intercept of the line
        """

        try:
            self.slope = float(slope)
        except ValueError:
            raise TypeError("invalid slope value '%s'" % slope)
        try:
            self.intercept = float(intercept)
        except ValueError:
            raise TypeError("invalid intercept value '%s'" % intercept)

    def __str__(self):
        """Returns a string representation of the line"""
        return "y = %f * x + %f" % (self.slope, self.intercept)

    def __call__(self, x):
        """Evaluates a line at a given position x"""
        assert isinstance(x, float)
        return self.slope * x + self.intercept

    def perpToAtX(self, x):
    
        """Returns a line perpendicular to this line at the given x position"""
        
        assert isinstance(x, float)
        perpSlope = -1.0 / self.slope
        perpIntercept = x * (self.slope + 1.0 / self.slope) + self.intercept
        return Line(perpSlope, perpIntercept)

    def perpToAtY(self, y):

        """Returns a line perpendicular to this line at the given x position"""

        assert isinstance(y, float)
        x = (y - self.intercept) / self.slope
        return self.perpToAtX(x)

    def flipXY(self):
        
        """Creates a line where x and y have been flipped"""
        
        if self.slope == 0.0:
            raise ZeroDivisionError("cannot flip line with slope = 0")

        newSlope = 1.0 / self.slope
        newIntercept = -self.intercept / self.slope
        return Line(newSlope, newIntercept)

class LinearFit(Line):

    """Class for describing linear fits"""
    
    def __init__(self, slope=0.0, intercept=0.0, r2=0.0):
    
        """
        Initializes a linear fit to have the given slope, intercept, and
        correlation coefficient.
        
        Input:  slope     -- slope of the line
                intercept -- intercept of the line
                r2        -- correlation coefficient of the line
        """

        Line.__init__(self, slope, intercept)

        try:
            self.r2 = float(r2)
        except ValueError:
            raise TypeError("invalid r2 value '%s'" % r2)

    def __str__(self):
        """Returns a string representation of the linear fit"""
        return "y = %f * x + %f, r^2 = %f" % (self.slope, self.intercept,
                                              self.r2)

