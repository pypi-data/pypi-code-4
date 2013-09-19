#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


__author__ = 'yarnaid'

import tools.convertion as convert
import pixelmap as pixelmap
import properties as properties
import os


class Alm(properties.Multipoled):

    name = None
    temp = True

    def get_attrs(self, **kwargs):
        res = {'lmax': self.lmax,
               'lmin': self.lmin}
        res.update(kwargs)
        return res

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if os.path.exists(self.name) and self.name.count('tmp') < 1:
            self.temp = False

    def __setattr__(self, name, value):
        if name == 'name' and os.path.exists(value) and value.count('tmp') < 1:
            self.__dict__['temp'] = False
        try:
            return super(Alm, self).__setattr__(name, value)
        except:
            self.__dict__[name] = value
        return value

    def __del__(self):
        if self.temp:
            os.remove(self.name)

    def to_map(self, map_name=None, **kwargs):
        attrs = self.get_attrs(**kwargs)
        attrs['name'] = convert.alm_to_map(
            self.name,
            map_name=map_name,
            **attrs
        )
        pmap = pixelmap.gPixelMap(**attrs)
        return pmap

    def smooth(self, smooth_window, smoothed_name=None, **kwargs):
        smoothed_name = convert.smooth_alm(
            self.name,
            smooth_window,
            smoothed_name=smoothed_name,
            **kwargs
        )
        attrs = self.get_attrs(kwargs)
        attrs['name'] = smoothed_name
        alm_smoothed = Alm(**attrs)
        self.name = smoothed_name
        return alm_smoothed

    def get_rotation(self, rotated_name=None, **kwargs):
        attrs = self.get_attrs(**kwargs)
        rotated_name = convert.rotate_alm(
            self.name,
            rotated_name=rotated_name,
            **attrs
        )
        attrs['name'] = rotated_name
        rotated_alm = Alm(**attrs)
        return rotated_alm

    def rotate(self, **kwargs):
        rotated = self.get_rotation(**kwargs)
        self.__dict__.update(rotated.get_attrs(**kwargs))
        self.name = rotated.name

    def to_cl(self, **kwargs):
        return convert.alm_to_cl(self.name, **self.get_attrs(**kwargs))

    def update_ls(self, update_name=None, **kwargs):
        self.name = convert.alm_update_ls(
            self.name, update_name, **self.get_attrs(**kwargs))
        return self.name
