import pynacolada as pcl
from Scientific.IO import NetCDF
import os
import numpy as np
import pylab as pl

R = 287.058

fnin = '/home/hendrik/data/belgium_aq/rcm/aq09/stage1/int2lm/laf2009010100_urb_ahf.nc'
#print fnin
# fobjin = open(fnin,'rb')
fin = NetCDF.NetCDFFile(fnin,'r')
fnout = '/home/hendrik/data/belgium_aq/rcm/aq09/stage1/int2lm/laf2009010100_urb_ahf3.nc'
os.system('rm '+fnout)
#print fnout
# fobjout = open(fnout,'wb+''rlat')
fout = NetCDF.NetCDFFile(fnout,'w')
datin =  [{'file': fin, \
           'varname': 'U', \
           'dsel': {'level' : range(30,40,1)}, \
           'daliases': { 'srlat':'rlat', 'srlon':'rlon' },\
          },\
          {'file': fin, \
           'varname':'V', \
           'dsel': {'level' : range(30,40,1)},
           'daliases': { 'srlat':'rlat', 'srlon':'rlon' },\
           }\
         ]
datout = [{'file': fout, \
           'varname': 'u'}]
# selection of function dimension input
func = lambda U,V: np.sqrt(U**2+V**2) 
dnamsel = ['level',]
pcl.pcl(func,dnamsel,datin,datout,appenddim=True)

fout.close()


fig = pl.figure()
fout = NetCDF.NetCDFFile(fnout,'r')
pl.imshow(fout.variables['T'][:].squeeze())
fig.show()
fout.close()
