# -*- coding: utf-8 -*-
#import os
__author__ = 'yarnaid'

try:
    import glespy.properties as properties
    import glespy.pixelmap as pixelmap
    import glespy.tools.convertion as conv
except:
    import properties


class PointSource(object):
    """
    Class for storing file with point sources and
    converting it
    """
    name = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


    def to_pixelmap(self, map_name=None, **kwargs):
        map_name = conv.points_to_map(self.name, **kwargs)
        attrs = kwargs.copy()
        attrs['name'] = map_name
        pixmap = pixelmap.gPixelMap(**attrs)
        return pixmap

    def show(self, **kwargs):
        self.to_pixelmap(**kwargs).show(**kwargs)

