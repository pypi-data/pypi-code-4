'''
@author: J.Akeret
'''

import numpy as np
import time, math,os

import pycuda.tools as tools
import pycuda.driver as driver

class Solver(object):
    """
    'Abstract' base class for gpu based solver implementations.
    
    """

    _MAX_BLOCKS_COUNT = 500
    _MAX_BLOCK_SIZE = 64

    _info = False

    _sourceModule = None
    _compiledKernel = None
    
    _timepoints = None
    
    _neq = None
    _nsystems = None
    _nresults = None
    
    # device used
    _device = None

    generator = None

    def __init__(self):
        """
        Constructor for the Solver.
        """
        
        device = os.getenv("CUDA_DEVICE")
        if(device==None):
            self._device = 0
        else:
            self._device = int(device)
        
    def _getOptimalGPUParam(self, compiledKernel = None):
        """
        Returns the optimal size of blocks and threads for the given compiled source
        
        :param compiledKernel: sourceModule
            The kernel to use to determine the optimal param config
            
        :returns: blocks, threads
        
        """
        if compiledKernel == None:
            compiledKernel = self._compiledKernel
         
        # less overhead with smaller blocksize - ignore occupancy..
        threads = min(driver.Device(self._device).max_registers_per_block/compiledKernel.num_regs, self._MAX_BLOCK_SIZE)
        
        # assign number of blocks
        if (self._nsystems%threads == 0):
            blocks = self._nsystems/threads
        else:
            blocks = self._nsystems/threads + 1
        
        return blocks, threads
    
    
    def solve(self, y0, t, args=None, timing=False, info=False, write_code=False, full_output=False, **kwargs):
        """
        Integrate a system of ordinary differential equations.

        Solves the initial value problem for stiff or non-stiff systems
        of first order ode-s::
    
            dy/dt = func(y,t0,...)
    
        where y can be a vector.
    
        :param y0: array
            Initial condition on y (can be a vector).
        :param t: array
            A sequence of time points for which to solve for y.  The initial
            value point should be the first element of this sequence.
        :param args: array
            Extra arguments to pass to function.
        :param timing: bool
            True if timing output should be printed
        :param info: bool
            True if additional infos should be printed
        :param write_code: bool
            True if the generated code should be written to the disk
        :param full_output: boolean
            True if to return a dictionary of optional outputs as the second output    
        :param use_jacobian: bool
            Flag indicating if a jacobian matrix is provided. Requires an 
            implementation in the kernel
        :param rtol, atol: float
            The input parameters rtol and atol determine the error
            control performed by the solver.  The solver will control the
            vector, e, of estimated local errors in y, according to an
            inequality of the form ``max-norm of (e / ewt) <= 1``,
            where ewt is a vector of positive error weights computed as:
            ``ewt = rtol * abs(y) + atol``
            rtol and atol can be either vectors the same length as y or scalars.
            Defaults to 1.49012e-8.
        :param h0: float, (0: solver-determined)
            The step size to be attempted on the first step.
        :param mxstep: integer, (0: solver-determined)
            Maximum number of (internally defined) steps allowed for each
            integration point in t.
        
        :returns:
        y : array, shape (len(t), len(y0))
            Array containing the value of y for each desired time in t,
            with the initial value y0 in the first row.
    
        infodict : dict, only returned if full_output == True
            Dictionary containing additional output information
    
            =========  ============================================================
            key        meaning
            =========  ============================================================
            'message'  message representing state of system
            'system'   index of system
            'nst'      cumulative number of time steps
            'nfe'      cumulative number of function evaluations for each time step
            'nje'      cumulative number of jacobian evaluations for each time step
            =========  ============================================================
    
        """
        self._info = info
        self._nsystems=y0.shape[0]
        self._neq = y0.shape[1]
        self._timepoints = np.array(t,dtype=np.float32)
        self._nresults = len(t)
        
        if(self._compiledKernel == None):
            #compile to determine blocks and threads
            if timing:
                start = time.time()
                
            self._sourceModule, self._compiledKernel = self._compile(write_code)
            if timing:
                print("CudaPyInt: compiling kernel took: {0} s").format(round((time.time()-start),4))
            
        
        blocks, threads = self._getOptimalGPUParam()
        if info:
            print("CudaPyInt: blocks: {0}, threads: {1}").format(blocks, threads)
            print("CudaPyInt: used memory local: {0}, shared: {1}, registers: {2}").format(self._compiledKernel.local_size_bytes, self._compiledKernel.shared_size_bytes, self._compiledKernel.num_regs)

            occ = tools.OccupancyRecord( tools.DeviceData(), threads=threads, shared_mem=self._compiledKernel.shared_size_bytes, registers=self._compiledKernel.num_regs )
            print("CudaPyInt: tb per mp: {0}, limited by: {1}, occupancy:{2}").format(occ.tb_per_mp, occ.limited_by, round(occ.occupancy, 4))


        if timing:
            start = time.time()
        
        # number of run_count
        run_count = int(math.ceil(blocks / float(self._MAX_BLOCKS_COUNT)))
        for i in xrange(run_count):

            if(i==run_count-1):
                runblocks = int(blocks % self._MAX_BLOCKS_COUNT)
                if(runblocks == 0):
                    runblocks = self._MAX_BLOCKS_COUNT
            else:
                runblocks = int(self._MAX_BLOCKS_COUNT)

            if info:
                print("CudaPyInt: Run {0} block(s).").format(runblocks)

            minIndex = self._MAX_BLOCKS_COUNT*i*threads
            maxIndex = minIndex + threads*runblocks
            runParameters = args[minIndex:maxIndex]
            runInitValues = y0[minIndex:maxIndex]
            
            values, outputs = self._solve_internal(runInitValues, runParameters, runblocks, threads, full_output=full_output, **kwargs)
            
            if(i==0):
                returnValue = values
                returnOutputs = outputs
            else:
                returnValue = np.append(returnValue,values,axis=0)
                returnOutputs = np.append(returnOutputs,outputs,axis=0)
        
        if timing:
            print("CudaPyInt: No of blocks: {0}, threads: {1}, systems: {2}, took: {3}s").format(blocks, threads, self._nsystems, round((time.time()-start),4))

        if full_output:
            return returnValue, returnOutputs
        
        return returnValue
    
    