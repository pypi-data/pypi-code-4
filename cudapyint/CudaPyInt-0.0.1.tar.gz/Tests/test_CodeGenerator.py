##!/usr/bin/env python
'''
@author: J.Akeret
'''

"""
py.test for the CodeGenerator module.

"""
import sys
import os
import numpy as np

#path magic
ex_path = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(ex_path+"/../"))

from cudapyint.CodeGenerator import CodeGenerator


class TestCodeGenerator(object):
    generator = None

    def setup(self):
        self.generator = CodeGenerator("dummy.cu", None)


    def test_create_constants_fields_int(self):
        constants = {"int_field": 1}
        self.generator.constants = constants
        
        code = self.generator._create_constants_fields()
        assert code != None
        assert code == "__constant__ int int_field;\n\n"
        

    def test_create_constants_fields_float(self):
        constants = {"float_field": 1.1}
        self.generator.constants = constants
        
        code = self.generator._create_constants_fields()
        assert code != None
        assert code == "__constant__ double float_field;\n\n"
        
    def test_create_constants_fields_None(self):
        constants = {"none_field": None}
        self.generator.constants = constants
        
        try:
            code = self.generator._create_constants_fields()
        except (AssertionError):
            assert True
        else:
            assert False
        
    def test_create_constants_fields_bool(self):
        constants = {"bool_field": True}
        self.generator.constants = constants
        
        try:
            code = self.generator._create_constants_fields()
        except (AssertionError):
            assert True
        else:
            assert False
        
    def test_create_constants_fields_long(self):
        constants = {"long_field": 1L}
        self.generator.constants = constants
        
        try:
            code = self.generator._create_constants_fields()
        except (AssertionError):
            assert True
        else:
            assert False
        
    def test_create_constants_fields_numpy_float32(self):
        constants = {"numpy_float32_array": np.arange(0,10,dtype=np.float32)}
        self.generator.constants = constants
        
        code = self.generator._create_constants_fields()
        assert code != None
        assert code == "__constant__ float numpy_float32_array[10];\n__constant__ int numpy_float32_array_len = 10;\n\n\n"
        

    def test_create_constants_fields_numpy_float64(self):
        constants = {"numpy_float64_array": np.arange(0,10,dtype=np.float64)}
        self.generator.constants = constants
        
        code = self.generator._create_constants_fields()
        assert code != None
        assert code == "__constant__ double numpy_float64_array[10];\n__constant__ int numpy_float64_array_len = 10;\n\n\n"
        
