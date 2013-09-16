'''
@author: J.Akeret
'''

import numpy as np

_SUPPORTED_SIMPLE_TYPES = [int, float, np.float32, np.float64]
_SUPPORTED_ARRAY_TYPES = [type(np.array([]))]
_SUPPORTED_DATA_TYPES = _SUPPORTED_SIMPLE_TYPES + _SUPPORTED_ARRAY_TYPES

_CONSTANT_KEY_WORD = "__constant__ "

class CodeGenerator(object):
    """
    Abstract code generator. Provides function for type conversion and file persisting
    """
    
    _SOURCE_FILE_NAME = "CudaPyInt_generated_code.cu"
    
    _DATA_TYPES ={int: "int",
                  float: "double",
                  np.float32: "float",
                  np.float64: "double",
                  np.dtype(np.float32): "float", 
                  np.dtype(np.float64): "double"}
    
    
    def __init__(self, cudaCodePath, constants):
        """
        Constructor for the ode solver.
    
        :param cudaCodePath: string
            Path to the cuda kernel.
        :param constants: dict
            Dictionary containing constants value used for the integration.
            Supported values are:
                int, float, numpy.float32, numpy.float64, numpy.array
        """
        self.constants = constants
        self.cudaCode = open(cudaCodePath,'r').read()
        
    
    def _writeCode(self, code):
        """
        Writes the given code to the disk
        
        :param code: string
            The code to be written
        """
        out = open(self._SOURCE_FILE_NAME,'w')
        print >>out, code
        
    def _create_constants_fields(self):
        """
        Generates CUDA C code to store the constants.
        The Python structures are automatically converted in C structures. See _SUPPORTED_DATA_TYPES for the supported data types
        
        :returns:
        Generated code for constants
        
        """
        constants = ""
        
        for key in self.constants:
            values = self.constants[key]
            assert type(values) in _SUPPORTED_DATA_TYPES, "The provided data type is not supported. Type " + str(type(values)) + " supported "+str(_SUPPORTED_DATA_TYPES)
            if(type(values) in _SUPPORTED_SIMPLE_TYPES):
                constants += _CONSTANT_KEY_WORD + self._DATA_TYPES[type(values)] +" " + key + ";\n"
            else:
                constants += _CONSTANT_KEY_WORD + self._DATA_TYPES[values.dtype] +" " + key + "[" + repr(len(values)) + "];\n"
                constants += _CONSTANT_KEY_WORD + "int " + key + "_len = " + repr(len(values)) + ";\n\n"
        
        constants += "\n"
        return constants
            
