#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# vim: tabstop=4 shiftwidth=4 expandtab


import numpy
import netCDF4


def homogeneous_drifters(latmin,lonmin,latmax,lonmax,z,ddeg):
    """
    """
    output = []
    for lon in numpy.arange(lonmin,lonmax+ddeg,ddeg):
        for lat in numpy.arange(latmin,latmax+ddeg,ddeg):
            output.append([lon,lat,z])
    return numpy.array(output)




#drfts = homogeneous_drifters(4,-50,6,-40, 25, 0.25)
drfts = homogeneous_drifters(15,-50,20,-40, 100, 2)


from netCDF4 import Dataset
rootgrp = Dataset('drifters_inp.nc', 'w', format='NETCDF3_CLASSIC')
print rootgrp.file_format

NP,ND = drfts.shape

nd = rootgrp.createDimension('nd', ND)
np = rootgrp.createDimension('np', NP)


ids = rootgrp.createVariable('ids','i4',('np',))
ids[:] = numpy.arange(NP)+1

positions = rootgrp.createVariable('positions','f8',('np','nd'))
positions.names = "i j"
positions.units = "- -"
#positions[:] = numpy.array([[280,480],[260,500],[180,360]])
#positions[:] = numpy.array([[480,280],[500,260],[360,180]])
#positions[:] = numpy.array([[-40,15,5],[-50,20,10],[-30,10,100]])
#positions[:] = numpy.array([[180, 90], [190, 110], [185, 100], [180, 95], [185, 110]])
positions[:] = drfts

rootgrp.velocity_names = "u v"
rootgrp.field_names = "lon lat temp salt"
rootgrp.field_units = "deg_N deg_E Celsius ppu"
rootgrp.time_units = "seconds"
rootgrp.title = "example of input data for drifters"


rootgrp.close()
