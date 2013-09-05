#!/usr/bin/env python

""" A Class to handle MOM4 outputs
"""

from pydap.client import open_url

class Model(object):

    def __init__(self, urlpath):
        self.data = open_url(urlpath)
        self._field = None

    @property
    def field(self):
        return self._field

    @field.setter
    def field(self, field):
        self._field = self.data[field]

    @property
    def lon(self):
        LON = self.field.dimensions[-1]
        return self.data[LON][:]

    @property
    def lat(self):
        LAT = self.field.dimensions[-2]
        return self.data[LAT][:]

    @property
    def depth(self):
        DEPTH = self.field.dimensions[-3]
        return self.data[DEPTH][:]

    @property
    def time(self):
        TIME = self.field.dimensions[-4]
        return [(v, self.data[TIME].units) for v in self.data[TIME][:]]


class MOM4p1(Model):

    def __init__(self, urlpath):
        print urlpath
        super(MOM4p1, self).__init__(urlpath)
        self.name = 'MOM4p1'

    def get_data(self, l0, j0, i0):
        return ma.masked_equal(
                self.field.array[l0:l0 + 2, :, j0:j0 + 2, i0:i0 + 2],
                self.field.missing_value)

from UserDict import UserDict
import numpy
from numpy import ma

class Modelo_from_dap(UserDict):
    """
    """
    def __init__(self,urlpath):
        """
        """
        from pydap.client import open_url
        self.data = {}

        self.dataset = open_url(urlpath)
        ## Dictionary with the reference data for the model
        ##print "Available: ",dataset_model.keys()
        #for v in ['time','xt_ocean','yt_ocean','st_ocean']:
        #    self.data[v] = ma.array(self.dataset[v][:])
        ## Adjust the grid to the regular [-180:180]
        #self.data['xt_ocean'][self.data['xt_ocean']<-180] = self.da
        return

    def keys(self):
        keys = self.data.keys()
        for k in self.dataset.keys():
	    if k not in keys:
	        keys.append(k)
        return keys

    def __getitem__(self,index):
        """
        """
	if index in self.data.keys():
            return self.data[index]

        if index not in self.keys():
	    return

	field = getattr(self.dataset, index)
	if (index,) == field.dimensions:
	    self.data[index] = ma.array(field[:])
	    self.data[index].attributes = field.attributes
	    return self.data[index]
	else:
	    # Not sure the best way to do it
	    # To be transparent I should get the data as an array
	    # But there is always the risk to bring eveything by mistake
	    self.data[index] = ma.masked_values(field[index][:],field.missing_value)
	    #self.data[index].attributes = field.attributes
	    print dir(field[index])


	return field

from UserDict import UserDict

class MAFromNC(object):
    """   
    """  
    def __init__(self, ref):
        self.ref = ref
        self.shape = self.ref.shape
        self.dtype = self.ref.dtype
        self.units = self.ref.units
        #self.copy = self[:].copy # Not sure if it will work
    def __getitem__(self, key):
        if hasattr(self.ref,'missing_value'):
            return ma.masked_values(self.ref[key], self.ref.missing_value)
        else:
            return ma.array(self.ref[key])
    #def __setitem__(self, key, value):
    #    if type(value) == numpy.ma.core.MaskedArray:
    #        #self.ref[key] = value.filled()
    #        tmp = value.data 
    #        tmp[value.mask] = self.ref._v_attrs.missing_value
    #        self.ref[key] = tmp
    #    else:
    #        self.ref[key] = value



import netCDF4
class Modelo_from_nc(dict):
    """
    """
    def __init__(self, ncfpath):
        """
        """
        super(Modelo_from_nc, self).__init__()
        self.dataset = netCDF4.Dataset(ncfpath)
        self.close = self.dataset.close
        self.data = {}
        self.loaddata()
    def loaddata(self):
        self._set_datetime()
        # Improve this. It should be in a conditional and load only when
        #   requested. For now, this will work
        for var in ['xu_ocean', 'yu_ocean', 'st_ocean', 'st_edges_ocean', 
          'xt_ocean', 'yt_ocean', 'sw_ocean', 'sw_edges_ocean', 'hu']:
            if var in self.dataset.variables.keys():
                self.data[var] = ma.array(self.dataset.variables[var][:])

    def _set_datetime(self):
        """
	    Should I really do it right the way, automatically?
        """
	if 'time' in self.dataset.variables:
	    from coards import from_udunits
	    self.data['datetime'] = ma.array([ from_udunits(v, self.dataset.variables['time'].units) for v in self.dataset.variables['time'][:] ])
	return
    def keys(self):
        keys = self.data.keys()
	for k in self.dataset.variables.keys():
	    if k not in keys:
	        keys.append(k)
        return keys
    def __getitem__(self,index):
        """
        """
        if index in self.data.keys():
            return self.data[index]
        else:
            self.data[index] = MAFromNC(self.dataset.variables[index])
            return self.data[index]
        field = self.dataset.variables[index]
        if (index,) == field.dimensions:
            self.data[index] = ma.array(field[:])
            self.data[index].units = field.units
            return self.data[index]
        else:
            # Need to be able to get only a slice before convert 
            #   to masked array, otherwise is a problem for huge
            #   files
            data = ma.masked_values(field[:], field.missing_value)
            data.units = field.units
            data.long_name = field.long_name
            data.dimensions = field.dimensions
            return data
        #    return self.data[index]
        return
    def get_data(self,index,slice):
        """
        """
        field = self.dataset.variables[index]
        return ma.masked_values(field[slice], field.missing_value)


class Model_profiles(Modelo_from_nc):
    """


    """
    def __init__(self, ncfpath):
        super(Model_profiles, self).__init__(ncfpath)
        self.data = Modelo_from_nc(ncfpath)
        self.keys = self.data.keys
        # Unfinished
        return

    def nearest_profile(self,t,lon,lat,var):
        """
        """
        # --- Model ----
        # Define the closest time instant
        #dt = self.['datetime']-t
        #nt = numpy.arange(dt.shape[0])[dt == min(dt)][0]
        nt = numpy.absolute(ma.array([d.toordinal() for d in self['datetime']])-t.toordinal()).argmin()
        # Define the nearest point
        nx = numpy.absolute(self['xt_ocean']-lon).argmin()
        ny = numpy.absolute(self['yt_ocean']-lat).argmin()
        # Extract the temperature profile from the model
        profile = ma.masked_values(self.dataset.variables[var][nt,:,ny,nx],value=self.dataset.variables[var].missing_value)
        # Restrict the profile to deeper than 10m, and only good data
        # The find_z20 can't handle masked arrays
        #ind = (temp_model.mask==False) & (numpy.absolute(self['depth'])>10)
        #z = model_ref['depth'][ind]
        #t = temp_model[ind]
        return {'depth':self['st_ocean'],var:profile,'lon':self['xt_ocean'][nx],'lat':self['yt_ocean'][ny]}
        #return profile

    def around_profile(self, t, lon, lat, var, rmax):
        """
        
            !!ATENTION!! There are a lot of problems on this approach for big distances,
              including the borders and the poles.

            Improve it to actually calculate the distances.
        """
        nt = numpy.absolute(ma.array([d.toordinal() for d in self['datetime']])-t.toordinal()).argmin()
        #from fluid.common.distance import distance
        #Lon, Lat = numpy.meshgrid(model_ref['xt_ocean'], model_ref['yt_ocean'])
        ##L = distance(lon = Lon, lat = Lat, lon_c = lon, lat_c = lat)
        #fac = numpy.cos((lat+Lat)/2.*numpy.pi/180)
        #L = ((Lat-lat)**2+((Lon-lon)*fac)**2)**.5
        #L = L*60*1852

        nX = numpy.arange(self['xt_ocean'].shape[0])[abs(self['xt_ocean']-lon)<(rmax/1856./60.)]
        nY = numpy.arange(self['yt_ocean'].shape[0])[abs(self['yt_ocean']-lat)<(rmax/1856./60.)]

        profile = {'depth':self['st_ocean']}
        profile['lon'] = self['xt_ocean'][nX[0]:nX[-1]+1]
        profile['lat'] = self['yt_ocean'][nY[0]:nY[-1]+1]

        profile[var] = ma.masked_values(self.dataset.variables[var][nt,:,nY[0]:nY[-1]+1,nX[0]:nX[-1]+1],value=self.dataset.variables[var].missing_value)
        #profile = ma.masked_values(self.dataset[var][nt,:,nY:nY+1,nX:nX+1],value=self.dataset[var].missing_value)

        return profile




class Modelo_from_nca(UserDict):
    """
    """
    def __init__(self,ncfpath):
        """
        """
        self.data = {}
        self.dataset = []
        for ncf in ncfpath:
            self.dataset.append(Modelo_from_nc(ncf))
        #
        self._build_time()
        return
    def _build_time(self):
        time = numpy.array([])
        mask = numpy.array([], dtype='bool')
	for d in self.dataset:
            time = numpy.append(time, d['time'].data)
            mask = numpy.append(mask, ma.getmaskarray(d['time']))
	self.data['time'] = ma.masked_array(time,mask)
    def keys(self):
        keys = self.data.keys()
	for k in self.dataset[0].keys():
	    if k not in keys:
	        keys.append(k)
        return keys
    def __getitem__(self,index):
        """
        """
        if index in self.data.keys():
            return self.data[index]
        if index not in self.keys():
            return

        dims = self.dataset[0].dataset.variables[index].dimensions
        if 'time' in dims:
            #if 'time' == dims[0]:
            data = numpy.array([])
            mask = numpy.array([], dtype='bool')
            for d in self.dataset:
                time = numpy.append(data, d[index].data)
                mask = numpy.append(mask, ma.getmaskarray(d[index]))
            return ma.masked_array(time,mask)
        else:
	    return self.dataset[0][index]


#ncfpath = ["/stornext/grupos/ocean/simulations/exp030/dataout/ic200701/ocean/CGCM/20070101.ocean_transport.nc", "/stornext/grupos/ocean/simulations/exp030/dataout/ic200701/ocean/CGCM/20080101.ocean_transport.nc"]
#reload(mom4)
#x = Modelo_from_nca(ncfpath)
#x.keys()
#x['xu_ocean']
#x['ty_trans']

##if __name__ == '__main__':
#urlpath="http://opendap.ccst.inpe.br/Models/CGCM2.1/exp030/20070101.ocean_transport.nc"
#from pydap.client import open_url
#dataset = open_url(urlpath)
#import mom4
#reload(mom4)
#x = mom4.Modelo_from_dap(urlpath = urlpath)
#print dir(x)

