import matplotlib
import mpl_toolkits.basemap as basemap

import scipy.interpolate as interp
import scipy.optimize as optim
import scipy.stats as stats
import scipy.signal as signal
import numpy as np
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import matplotlib.axes as pltax
import matplotlib.gridspec as gridspec

import realizations_tools as rt
import multiprocessing as mproc
import moisture_tools as mt

from netCDF4 import MFDataset,Dataset,num2date,date2num
from datetime import  datetime

import textwrap

import glob

def recover_time(file):
    data=Dataset(file)
    time_axis=(num2date(data.variables['time'],
                                 units=data.variables['time'].units,
                                 calendar=data.variables['time'].calendar)
                    )
    name_axis=np.array([file for item in time_axis])
    data.close()
    return time_axis,name_axis

def main(source_files):
    time_axis, name_axis=map(np.concatenate,
                             zip(*map(recover_time,source_files))
                             )
    sort_id=np.argsort(time_axis)
    
    data=Dataset(name_axis[sort_id][0])

    var_list={ 'TMP_L100':'ta', 'SPF_H_L100':'hus', 'V_VEL_L100':'wa', 'V_GRD_L100':'va'}
    for var in var_list.keys():
        output=Dataset('test/'+var_list[var]+'.gdas.19790101-20101231.nc','w',format='NETCDF4')
        replicate_netcdf_file(output,data)
        output.createDimension('time',len(time_axis))
        time = output.createVariable('time','d',('time',))
        time.calendar=data.variables['time'].calendar
        time.units=data.variables['time'].units
        time[:]=date2num(time_axis[sort_id],units=time.units,calendar=time.calendar)

        replicate_netcdf_var(output,data,var_list,var)
        ptr_group=output.createGroup('pointers')
        pointers=ptr_group.createVariable(var_list[var],str,('time',),zlib=True)
        for id, name in enumerate(name_axis[sort_id]): pointers[id]=str(name)

        output.sync()
        output.close()
    data.close()
    return


def replicate_netcdf_file(output,data):
    for att in data.ncattrs():
        att_val=getattr(data,att)
        if 'encode' in dir(att_val):
            att_val=att_val.encode('ascii','replace')
        setattr(output,att,att_val)
    output.sync()
    return output

def replicate_netcdf_var(output,data,var_list,var):
    for dims in data.variables[var].dimensions:
        if dims not in output.dimensions.keys():
            output.createDimension(dims,len(data.dimensions[dims]))
            dim_var = output.createVariable(dims,'d',(dims,))
            dim_var[:] = data.variables[dims][:]
            output = replicate_netcdf_var(output,data,{dims:dims},dims)

    if var not in output.variables.keys():
        output.createVariable(var_list[var],'d',data.variables[var].dimensions)
    for att in data.variables[var].ncattrs():
        att_val=getattr(data.variables[var],att)
        if att[0]!='_':
            if 'encode' in dir(att_val):
                att_val=att_val.encode('ascii','replace')
            setattr(output.variables[var_list[var]],att,att_val)
    output.sync()
    return output

if __name__ == "__main__":
    name_list=['pgbhnl','pgbh01','pgbh02','pgbh03','pgbh04','pgbh05']
    source_files=[]
    for name_id in name_list:
        source_files.extend(glob.glob(name_id+'.gdas.*.nc'))
    main(source_files)
