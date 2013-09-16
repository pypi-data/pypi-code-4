'''
@author: J.Akeret
'''

import cudapyint
import numpy as np

class ParallelODESolver(cudapyint.ODESolver):
    """
    Extension of the ODESolver for parallel computation of the equations within one ODE System
    """
    
    _CULSODA_MAIN_FILE_NAME = "cuLsoda_main_parallel.cu"
    
    def __init__(self, cudaCodePath, constants, compile_options=None, threads=1):
        """
        Constructor for the ode solver.
    
        :param cudaCodePath: string
            Path to the cuda kernel.
        :param constants: dict
            Dictionary containing constants value used for the integration.
            Supported values are:
                int, float, numpy.float32, numpy.float64, numpy.array
        :param compile_options: list (optional)
            List of options passed to the compiler
        :param threads: int (optional)
            number of threads to be used per ODE system
        """
        super(ParallelODESolver, self).__init__(cudaCodePath, constants, compile_options)
        self.threads = threads
    
    
        # method for calculating optimal number of blocks and threads per block
    def _getOptimalGPUParam(self, compiledRunMethod = None):
        """
        Returns the optimal configration. For the parallel execution the number of 
        threads is given by the user and the number of blocks is given by the number of ODE systems
        """
        return self._nsystems, self.threads


    def _post_process_results(self, results, info, nsystems, blocks, threads, full_output):
        """
        Removes duplicated entries from the integrations since multiple threads per ODE system are launched
        """
        values = np.empty([blocks, self._nresults, self._neq])
        
        for i in xrange(blocks):
            values[i] = results[i*threads]

        if(full_output):
            return values, info
            
        return values
