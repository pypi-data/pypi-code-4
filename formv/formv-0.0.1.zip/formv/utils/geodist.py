#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import math

class GeoDistance():
    def __init__(self, origin, destination):
        self.earth_radius = 6371 # - km
        self.o = origin
        self.d = destination        

    def haversine(self):
        """ http://en.wikipedia.org/wiki/Haversine_formula """
        lat1, lon1 = self.o; lat1 = float(lat1); lon1 = float(lon1)
        lat2, lon2 = self.d; lat2 = float(lat2); lon2 = float(lon2)
    
        dlat = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) *
             math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2))
        c = (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))
        d = (self.earth_radius * c)
        return d