'''
@author: J.Akeret
'''

import cudapyint.CodeGenerator as generator
import os

class CulsodaCodeGenerator(generator.CodeGenerator):
    """
    Extends the cudapyint.CodeGenerator in order to generate Culsoda specific code.
    
    """
    
    def __init__(self, cudaCodePath, constants, culsoda_file_name, culsoda_main_file_name, args_tex_name):
        """
        Constructor for the ode solver.
    
        :param cudaCodePath: string
            Path to the cuda kernel.
        :param constants: dict
            Dictionary containing constants value used for the integration.
            Supported values are:
                int, float, numpy.float32, numpy.float64, numpy.array
        :param culsoda_file_name: string
            name of the culsoda source file
        :param culsoda_main_file_name: string
            name of the culsoda main source file
        :param args_tex_name: string
            name of the arguments texture
            
        """
        super(CulsodaCodeGenerator, self).__init__(cudaCodePath, constants)
        self.culsoda_file_name = culsoda_file_name
        self.culsoda_main_file_name = culsoda_main_file_name
        self.args_tex_name = args_tex_name
        
    def generate(self, neq=1, blocks=1, threads=1, write_code=False):
        """
        Generates the complete culsoda code
        
        :param blocks: int (optional)
            The number of blocks
            
        :param threads: int (optional)
            The number of threads / block
        :param write_code: bool (optional)
            True if the generated code should be written to the disc
            
        :returns:
        The generated code
        """
        fc = open( os.path.join(os.path.split(os.path.realpath(__file__))[0],self.culsoda_file_name),'r')
        coulsoda_source = fc.read()
        
        fc = open( os.path.join(os.path.split(os.path.realpath(__file__))[0],self.culsoda_main_file_name),'r')
        culsoda_main_source = fc.read()
        
        block_size_def = "#define BLOCK_SIZE " + repr(threads) + "\n"
        neq_def = "#define NEQ " + repr(neq) + "\n"
        
        definitions = block_size_def + neq_def + "\n"
    
        args_array_def = "texture<float, 2, cudaReadModeElementType> "+ self.args_tex_name +";\n\n"

        constants_def= self._create_constants_fields()

        common_block_def = "__device__ struct cuLsodaCommonBlock common[" + repr(blocks*threads) + "];\n"
        code_def =  definitions + args_array_def + constants_def + self.cudaCode + coulsoda_source + common_block_def + culsoda_main_source
        
        if (write_code):
            self._writeCode(code_def)
        
        return code_def
    
