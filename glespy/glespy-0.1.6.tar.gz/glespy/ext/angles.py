#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'yarnaid'


class Zone(object):

    """
    Zones for using with GlesPy
    LAT1,LON1,LAT2,LON2 or LAT,LON[,RADIUS]
    in degrees
    """
    angles = None

    def __init__(self, *args):
        super(Zone, self).__init__()
        if 2 > len(args) or len(args) > 4:
            raise IndexError(
                '*args number must be int [2, 3, 4] for circle or rectangle, {} got'.format(len(args)))
        if len(args) == 2:
            args += (90,)
        self.angles = args

    def __repr__(self):
        return 'd,'.join(map(str, self.angles)) + 'd'

    def __call__(self):
        return self.__repr__()

    def __invert__(self):
        """
        circle moves to dipole side
        rectangle save LAT1,LON1 and size changes direction
        """
        if len(self.angles) == 3:
            self.angles[0] = -self.angles[0]
            self.angles[1] += 180
            self.angles[2] = 180 - self.angles[2]
        if len(self.angles) == 4:
            self.angles[2] = self.angles[0] -\
                abs(self.angles[2] - self.angles[0])
            self.angles[3] = self.angles[1] -\
                abs(self.angles[3] - self.angles[1])


class Angle(object):

    """
    An angle of theta and phi
    """
    theta = None
    phi = None
    __deg = '{}d'

    def __init__(self, *args):
        super(Angle, self).__init__()
        if len(args) != 2:
            raise IndexError(
                '*args number must be 2, {} got'.format(len(args)),
            )
        self.theta = args[0]
        self.phi = args[1]

    def __invert__(self):
        """
        get an angle to opposite dipole side
        """
        return Angle(-self.theta, 180 + self.phi)

    def __add__(self, other):
        return Angle(self.theta + other.theta, self.phi + other.phi)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return Angle(self.theta - other.theta, self.phi - other.phi)

    # def __rsub__(self, other):
        # return self.__add__(-other)

    def __neg__(self):
        return Angle(-self.theta, -self.phi)

    def __pos__(self):
        return self

    def phi_d(self):
        return self.__deg.format(self.phi)

    def theta_d(self):
        return self.__deg.format(self.theta)
