#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


__author__ = 'yarnaid'


class Printable(object):
    def __repr__(self):
        vals = []
        for k, v in self.__dict__.items():
            if k[0] != '_' and v not in ['', None]:
                vals.append('{}={}'.format(k, v))
        res = '<{}: {}>'.format(self.__class__.__name__, ', '.join(vals))
        return res

class Multipoled(Printable):

    """
    Class that has multipoles propreties
    """
    lmax = 1
    lmin = 0

    def __setattr__(self, name, value):
        if (name in ['lmax', 'lmin']) and (not isinstance(value, int)):
            raise ValueError('Multipoles must be an integer')
        self.__dict__[name] = max(0, value)
        self.__update_lmax()

    def __update_lmax(self):
        if self.lmin > self.lmax:
            self.__dict__['lmax'] = self.lmin


class Rendered(Multipoled):

    """
    Class with nx and np
    np >= nx * 2 >= lmax * 2 + 1 >= lmin
    """
    nx = 0
    np = 0

    def __init__(self, **kwargs):
        super(Rendered, self).__init__()
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __setattr__(self, name, value):
        if (name in ['nx', 'np']) and (not isinstance(value, int)):
            raise ValueError('Map size must be an integer')
        self.__dict__[name] = value
        self.__update_data()
        self.__update_data_reverse()

    def __update_data(self):
        if self.lmin > self.lmax:
            self.__dict__['lmax'] = self.lmin
        if self.lmax * 2 + 1 > self.nx:
            self.__dict__['nx'] = self.lmax * 2 + 1
        if self.nx * 2 > self.np:
            self.__dict__['np'] = self.nx * 2

    def __update_data_reverse(self):
        if self.nx < 4:
            self.__dict__['nx'] = int(self.np / 2)
        if self.lmax < 2:
            self.__dict__['lmax'] = int((self.nx - 1) / 2)
