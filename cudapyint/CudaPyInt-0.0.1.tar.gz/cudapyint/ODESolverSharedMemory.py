'''
@author: J.Akeret
'''

import cudapyint

class ODESolverSharedMemory(cudapyint.ODESolver):
    """
    Extends the ODESolver the enable CUDA shared memory.
    """
    
    _CULSODA_MAIN_FILE_NAME = "cuLsoda_main_shared_mem.cu"
    


