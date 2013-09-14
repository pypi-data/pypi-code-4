#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'yarnaid'

import properties as properties
import tools.convertion as conv
import alm
from ext import angles


class gPixelMap(properties.Rendered):

    """
    Class with lmax, lmin, nx, np attributes for map rendering
    """
    name = None
    temp = None

    def __init__(self, **kwargs):
        # super(gPixelMap, self).__init__(**kwargs)
        if self.name:
            self.temp = False
        else:
            self.temp = True
        for k, v in kwargs.items():
            setattr(self, k, v)
        pass

    def unset_temp(self):
        self.temp = False

    def __setattr__(self, name, value):
        try:
            return super(gPixelMap, self).__setattr__(name, value)
        except:
            self.__dict__[name] = value

    def from_alm(self):
        pass

    def __del__(self):        # todo: test
        if self.temp:
            pass
            # os.remove(self.name)

    def show(self, **kwargs):
        # todo: test
        conv.show_map(self.name, **kwargs)

    def add_map(self, other, **kwargs):
        try:
            other_name = other.name
        except AttributeError:
            other_name = other
        except:
            raise ValueError(
                'Can not sum PixelMap with {}'.format(type(other)))
        self.name = conv.sum_map(self.name, other_name, **kwargs)

    def __add__(self, other):
        attrs = self.get_attrs()
        attrs['name'] = conv.sum_map(self.name, other.name)
        return gPixelMap(**attrs)

    def __invert__(self):
        inverted = conv.mult_map(
            map_name=self.name,
            mult=-1,
        )
        attrs = self.get_attrs()
        attrs['name'] = inverted
        return gPixelMap(**attrs)

    def __neg__(self):
        return self.__invert__()

    def __sub__(self, other):
        attrs = self.get_attrs()
        attrs['name'] = conv.sum_map(self.name, other.name, mult=[1, 1])
        return gPixelMap(**attrs)

    def mult_number(self, other, **kwargs):
        attrs = self.get_attrs()
        attrs['name'] = conv.mult_map(self.name, other, **kwargs)
        return gPixelMap(**attrs)

    def __mul__(self, other):
        res = None
        if isinstance(other, (float, int,)):
            res = self.mult_number(other)
        return res

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        return self.__mul__(other ** (-1))

    def get_attrs(self, **kwargs):
        res = {'nx': self.nx,
               'np': self.np,
               'lmax': self.lmax,
               'lmin': self.lmin,
               }
        res.update(kwargs)
        return res

    def get_keep_zone(self, zone, cutted_map=None, **kwargs):
        attrs = self.get_attrs(**kwargs)
        cutted_map = conv.cut_map_zone(
            map_name=self.name,
            zone=zone,
            cutted_map=cutted_map,
            **attrs
        )
        attrs['name'] = cutted_map
        return gPixelMap(**attrs)

    def get_half(self, lat, lon, map_name=None, **kwargs):
        return self.get_keep_zone(
            angles.Zone(lat, lon),
            cutted_map=map_name,
            **kwargs
        )

    def get_top(self, top_name=None, **kwargs):
        return self.get_half(-90, 0, top_name, **kwargs)

    def get_bottom(self, bottom_name=None, **kwargs):
        return self.get_half(90, 0, bottom_name, **kwargs)

    def get_reflection(self, rtype, reflected_name=None, **kwargs):
        attrs = self.get_attrs(**kwargs)
        reflected_name = conv.reflect_map(map_name=self.name,
                                          rtype=rtype,
                                          reflected_name=reflected_name,
                                          **attrs
                                          )
        attrs['name'] = reflected_name
        return gPixelMap(**attrs)

    def to_alm(self, alm_name=None, **kwargs):
        attrs = self.get_attrs(**kwargs)
        alm_name = conv.map_to_alm(self.name, alm_name, **attrs)
        attrs['name'] = alm_name
        return alm.Alm(**attrs)

    def to_cl(self, cl_name=None, **kwargs):
        return self.to_alm(**kwargs).to_cl()

    def get_masked(self, mask_name, masked_map_name=None, **kwargs):
        attrs = self.get_attrs(**kwargs)
        masked_map_name = conv.mask_map(
            self.name,
            mask_name,
            masked_map_name,
            **attrs
        )
        attrs['name'] = masked_map_name
        masked_map = gPixelMap(**attrs)
        return masked_map
