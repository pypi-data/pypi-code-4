'''
@author: J.Akeret
'''

import cudapyint

class ParallelODESolverSharedMemory(cudapyint.ParallelODESolver):
    """
    Extends the ParallelODESolver the enable CUDA shared memory.
    """
    
    _CULSODA_MAIN_FILE_NAME = "cuLsoda_main_parallel_shared_memory.cu"
    
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
        super(ParallelODESolverSharedMemory, self).__init__(cudaCodePath, constants, compile_options)
        self.threads = threads
    
    
