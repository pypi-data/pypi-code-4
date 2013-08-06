import numpy as np
from netCDF4 import MFDataset,Dataset,num2date,date2num

def recover_time(file):
    file_name=file.split('|')[0]
    start_id=int(file.split('|')[1])
    end_id=int(file.split('|')[2])

    data=Dataset(file_name)
    time_axis=(num2date(data.variables['time'],
                                 units=data.variables['time'].units,
                                 calendar=data.variables['time'].calendar)
                    )[start_id:end_id]
    name_axis=np.array([file_name for item in time_axis])
    data.close()
    return time_axis,name_axis

def main(source_files):
    time_axis, name_axis=map(np.concatenate,
                             zip(*map(recover_time,source_files))
                             )
    sort_id=np.argsort(time_axis)
    
    data=Dataset(name_axis[sort_id][0])

    vars_to_copy=[var for var in data.variables.keys() if var not in data.dimensions.keys()]
    for var in vars_to_copy:
        output=Dataset('test/'+var+'.nc','w',format='NETCDF4')
        replicate_netcdf_file(output,data)
        output.createDimension('time',len(time_axis))
        time = output.createVariable('time','d',('time',))
        time.calendar=str(data.variables['time'].calendar)
        time.units=str(data.variables['time'].units)
        time[:]=date2num(time_axis[sort_id],units=time.units,calendar=time.calendar)

        replicate_netcdf_var(output,data,var)
        ptr_group=output.createGroup('pointers')
        pointers=ptr_group.createVariable(var,str,('time',),zlib=True)
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

def replicate_netcdf_var(output,data,var):
    for dims in data.variables[var].dimensions:
        if dims not in output.dimensions.keys():
            output.createDimension(dims,len(data.dimensions[dims]))
            dim_var = output.createVariable(dims,'d',(dims,))
            dim_var[:] = data.variables[dims][:]
            output = replicate_netcdf_var(output,data,dims)

    if var not in output.variables.keys():
        output.createVariable(var,'d',data.variables[var].dimensions)
    for att in data.variables[var].ncattrs():
        att_val=getattr(data.variables[var],att)
        if att[0]!='_':
            if 'encode' in dir(att_val):
                att_val=att_val.encode('ascii','replace')
            setattr(output.variables[var],att,att_val)
    output.sync()
    return output

if __name__ == "__main__":
    import argparse 
    import textwrap

    #Option parser
    description=textwrap.dedent('''\
    This script creates a virtual netcdf4 dataset.
    ''')
    epilog='Frederic Laliberte, Paul Kushner 07/2013'
    version_num='0.1'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                            description=description,
                            version='%(prog)s '+version_num,
                            epilog=epilog)

    parser.add_argument('source_files',nargs='+',
                         help='Source files and indices separated by \'|\'.')
    options=parser.parse_args()
    main(options.source_files)
