# ----------------------------------------
# Copyright (C) 2010-2011  Frank Paehlke
#
# This file is part of TourEditor.
#
# TourEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TourEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TourEditor.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------

import math

# ----------------------------------------

class TFLength:
    "Target function: Total length of graph"

    # L = sqrt(x^2+y^2)
    # dL/dx = 2x / 2 L = x/L
    # d2L/dx2 = (1 * L - x * x/L) / L^2 = (L^2-x^2)/L^3 = y^2/L^3

    @staticmethod
    def f (X, Y):
        assert len(X) == len(Y)
        n = len(X)-1
        res = 0.0
        for i in range(n):
            dx = X[i+1] - X[i]
            dy = Y[i+1] - Y[i]
            res += math.hypot (dx, dy)
        return res

    @staticmethod
    def dfdX (X, Y, i):
        "df(X,Y)/dX[i]"
        assert len(X) == len(Y)
        n = len(X)-1
        res = 0.0
        if i > 0:
            dx = X[i] - X[i-1]
            dy = Y[i] - Y[i-1]
            res += dx / math.hypot (dx, dy)
        if i < n:
            dx = X[i] - X[i+1]
            dy = Y[i] - Y[i+1]
            res += dx / math.hypot (dx, dy)
        return res

    @staticmethod
    def dfdY (X, Y, i):
        "df(X,Y)/dY[i]"
        assert len(X) == len(Y)
        n = len(X)-1
        res = 0.0
        if i > 0:
            dx = X[i] - X[i-1]
            dy = Y[i] - Y[i-1]
            res += dy / math.hypot (dx, dy)
        if i < n:
            dx = X[i] - X[i+1]
            dy = Y[i] - Y[i+1]
            res += dy / math.hypot (dx, dy)
        return res

    @staticmethod
    def d2fdXX (X, Y, i):
        "d^2f(X,Y)/dX[i]dX[i]"
        assert len(X) == len(Y)
        n = len(X)-1
        res = 0.0
        if i > 0:
            dx = X[i] - X[i-1]
            dy = Y[i] - Y[i-1]
            h = math.hypot (dx, dy)
            res += dy*dy / (h*h*h)
        if i < n:
            dx = X[i] - X[i+1]
            dy = Y[i] - Y[i+1]
            h = math.hypot (dx, dy)
            res += dy*dy / (h*h*h)
        return res

    @staticmethod
    def d2fdYY (X, Y, i):
        "d^2f(X,Y)/dY[i]dY[i]"
        assert len(X) == len(Y)
        n = len(X)-1
        res = 0.0
        if i > 0:
            dx = X[i] - X[i-1]
            dy = Y[i] - Y[i-1]
            h = math.hypot (dx, dy)
            res += dx*dx / (h*h*h)
        if i < n:
            dx = X[i] - X[i+1]
            dy = Y[i] - Y[i+1]
            h = math.hypot (dx, dy)
            res += dx*dx / (h*h*h)
        return res

# ----------------------------------------

class TFD2Square:
    "Target function: Square sum of 2nd derivative"

    @staticmethod
    def f (X, Y):
        """
The target function:
tf(X,Y) = sum ((2*X[i] - X[i-1] - X[i+1])^2, i=1..n-1)
        + sum ((2*Y[i] - Y[i-1] - Y[i+1])^2, i=1..n-1)
"""
        n = len(X)-1
        res = 0.0
        for i in range(1, n):
            a = 2*X[i] - X[i-1] - X[i+1]
            res += a*a
            a = 2*Y[i] - Y[i-1] - Y[i+1]
            res += a*a
        return res;

    @staticmethod
    def dfdX (X, Y, i):
        "df(X,Y)/dX[i]"
        n = len(X)-1
        if i < 0 or i > n:
            return None
        elif n < 2:
            return 0
        elif i == 0:
            return X[0] - 2*X[1] + X[2]
        elif i == 1:
            return -2*X[0] + 5*X[1] - 4*X[2] + X[3]
        elif i == n-1:
            return X[i-2] - 4*X[i-1] + 5*X[i] - 2*X[i+1]
        elif i == n:
            return X[i-2] - 2*X[i-1] + X[i]
        else:
            return X[i-2] - 4*X[i-1] + 6*X[i] - 4*X[i+1] + X[i+2]

    @staticmethod
    def dfdY (X, Y, i):
        "df(X,Y)/dY[i]"
        n = len(Y)-1
        if i < 0 or i > n:
            return None
        elif n < 2:
            return 0
        elif i == 0:
            return Y[0] - 2*Y[1] + Y[2]
        elif i == 1:
            return -2*Y[0] + 5*Y[1] - 4*Y[2] + Y[3]
        elif i == n-1:
            return Y[i-2] - 4*Y[i-1] + 5*Y[i] - 2*Y[i+1]
        elif i == n:
            return Y[i-2] - 2*Y[i-1] + Y[i]
        else:
            return Y[i-2] - 4*Y[i-1] + 6*Y[i] - 4*Y[i+1] + Y[i+2]

    @staticmethod
    def d2fdXX (X, Y, i):
        "d^2f(X,Y)/dX[i]dX[i]"
        n = len(X) - 1
        if i < 0 or i > n:
            return None
        if n < 2:
            return 0
        elif i == 0 or i == n:
            return 1
        elif i == 1 or i == n-1:
            return 5
        else:
            return 6

    @staticmethod
    def d2fdYY (X, Y, i):
        "d^2f(X,Y)/dY[i]dY[i]"
        n = len(Y) - 1
        if i < 0 or i > n:
            return None
        if n < 2:
            return 0
        elif i == 0 or i == n:
            return 1
        elif i == 1 or i == n-1:
            return 5
        else:
            return 6

# ----------------------------------------

class TourFileSmooth:

    def __init__ (self, targetfunction):
        self.f = targetfunction.f
        self.dfdX = targetfunction.dfdX
        self.dfdY = targetfunction.dfdY
        self.d2fdXX = targetfunction.d2fdXX
        self.d2fdYY = targetfunction.d2fdYY

    def smooth (self, X, Y, maxdeltaX, maxdeltaY, accuracy=1e-5, fixed=set()):
        """
minimize f(X) under the condition (res[i]-X[i] <= maxdelta)

tf(X) is minimized using an iterative algorithm until the
maximum change to any X[i] between two subsequent iterations
is smaller than maxdelta*accuracy
"""
        assert len(X) == len(Y)
        n = len(X) - 1
        if n < 2:
            return X, Y

        # normalize X, Y such that maxdelta=1
        X = [x / maxdeltaX for x in X]
        Y = [y / maxdeltaY for y in Y]
        # make a copy of X and Y
        resX = X[:]
        resY = Y[:]
        #print [('%.5f' % x) for x in resX], [('%.5f' % y) for y in resY]

        maxcorr = float('inf') # maximum correction
        while maxcorr >= accuracy:
            maxcorr = 0.0
            for i in range(1, n):
                if i in fixed:
                    continue
                # correct X[i]
                df = self.dfdX (resX, resY, i)
                d2f = self.d2fdXX (resX, resY, i)
                # correction term
                if df == 0.0 or d2f == 0.0:
                    continue
                resX_i = resX[i] - df/d2f
                # border condition
                if resX_i < X[i] - 1:
                    resX_i = X[i] - 1
                elif resX_i > X[i] + 1:
                    resX_i = X[i] + 1
                # maximum correction?
                corr = abs (resX_i - resX[i])
                if corr > maxcorr:
                    maxcorr = corr
                resX[i] = resX_i
                # correct Y[i]
                df = self.dfdY (resX, resY, i)
                d2f = self.d2fdYY (resX, resY, i)
                # correction term
                resY_i = resY[i] - df/d2f
                # border condition
                if resY_i < Y[i] - 1:
                    resY_i = Y[i] - 1
                elif resY_i > Y[i] + 1:
                    resY_i = Y[i] + 1
                # maximum correction?
                corr = abs (resY_i - resY[i])
                if corr > maxcorr:
                    maxcorr = corr
                resY[i] = resY_i
            #print [('%.5f' % x) for x in resX], [('%.5f' % y) for y in resY], maxcorr, accuracy

        # de-normalize X, Y
        return [x * maxdeltaX for x in resX], [y * maxdeltaY for y in resY]

# ----------------------------------------
