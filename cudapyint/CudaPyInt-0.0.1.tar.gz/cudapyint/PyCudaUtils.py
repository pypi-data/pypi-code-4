'''
@author: J.Akeret
'''

import pycuda.driver as driver

def create_2D_array( mat ):
    """
    Creates a 2D array on the GPU which can be used to assign texture memory from 2D numpy array
    
    :param mat: the 2D array to use
    """
    descr = driver.ArrayDescriptor()
    descr.width = mat.shape[1]
    descr.height = mat.shape[0]
    descr.format = driver.dtype_to_array_format( mat.dtype )
    descr.num_channels = 1
    descr.flags = 0
    ary = driver.Array(descr)
    return ary

def copy2D_host_to_array(arr, host, width, height ):
    """
    Copies the array from the host to the device
    
    :param arr: the GPU array
    :param host: the source on the host
    :param width: width of the array
    :param height: height of the array
    """
    copy = driver.Memcpy2D()
    copy.set_src_host(host)
    copy.set_dst_array(arr)
    copy.height = height
    copy.width_in_bytes = copy.src_pitch = width
    copy.height = height
    copy(aligned=True)
    
def copy_host_to_device(src):
    """
    Allocates the memory on the device and copies the data
    
    :param src: the source data structure
    
    :returns: 
    y: handle to data structure on device
    """
    dst =  driver.mem_alloc(src.size * src.dtype.itemsize)
    driver.memcpy_htod(dst, src)
    return dst

