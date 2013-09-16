##!/usr/bin/env python
'''
@author: J.Akeret
'''

"""
py.test for the CulsodaCodeGenerator module.

"""
import sys
import os
import numpy as np

#path magic
ex_path = os.path.realpath(os.path.dirname(__file__))
sys.path.append(os.path.realpath(ex_path+"/../"))

from cudapyint.CulsodaCodeGenerator import CulsodaCodeGenerator


class TestCulsodaCodeGenerator(object):
    _CULSODA_FILE_NAME = "../cudapyint/cuLsoda_all.cu"
    _CULSODA_MAIN_FILE_NAME = "../cudapyint/cuLsoda_main.cu"
    _ARGS_TEX_NAME = "args_tex"

    generator = None

    def setup(self):

        self.generator = CulsodaCodeGenerator("dummy.cu", {}, self._CULSODA_FILE_NAME, self._CULSODA_MAIN_FILE_NAME, self._ARGS_TEX_NAME)


    def test_generate_culsoda_coda(self):
        code = self.generator.generate(neq=1, blocks=1, threads=1, write_code=False)
        assert code != None
        assert code.find("dlsoda_") != 1
        assert code.find("cuLsoda") != 1
        
    def test_generate_texture(self):
        code = self.generator.generate(neq=1, blocks=1, threads=1, write_code=False)
        assert code != None
        assert code.find("texture<float, 2, cudaReadModeElementType> "+ self._ARGS_TEX_NAME) != 1
        
        
    def test_generate_common_block(self):
        code = self.generator.generate(neq=1, blocks=1, threads=1, write_code=False)
        assert code != None
        assert code.find("__device__ struct cuLsodaCommonBlock common") != 1
        
    def test_generate_macros(self):
        threads = 5
        neq = 2
        code = self.generator.generate(neq=1, blocks=1, threads=threads, write_code=False)
        assert code != None
        assert code.find("#define BLOCK_SIZE " + str(threads)) != 1
        assert code.find("#define NEQ " + str(neq)) != 1
        
        
