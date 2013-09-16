'''
@author: J.Akeret
'''

import cudapyint.CulsodaCodeGenerator as generator
import cudapyint.Solver as solver
import cudapyint.PyCudaUtils as utils

import pycuda.driver as driver
from pycuda.compiler import SourceModule
import pycuda.autoinit

import numpy as np

class ODESolver(solver.Solver):
    """
    Solver implementation to solve ODE using CULSODA. 
    Manages the compilation and execution of the CUDA kernel
    """
    
    IN_ISTATE_FIRST_CALL = 1
    IN_ISTATE_CONTIUNE = 2
    
    OUT_ISTATE_NOTHING_DONE = 1
    OUT_ISTATE_SUCCESSFULL = 2
    OUT_ISTATE_EXCESSIVE_WORK = -1
    
    _MSGS = {OUT_ISTATE_NOTHING_DONE: "nothing was done; TOUT = T",
             OUT_ISTATE_SUCCESSFULL: "Integration successful.",
         OUT_ISTATE_EXCESSIVE_WORK: "Excess work done on this call (perhaps wrong Dfun type).",
         -2: "Excess accuracy requested (tolerances too small).",
         -3: "Illegal input detected (internal error).",
         -4: "Repeated error test failures (internal error).",
         -5: "Repeated convergence failures (perhaps bad Jacobian or tolerances).",
         -6: "Error weight became zero during problem.",
         -7: "Internal workspace insufficient to finish (internal error)."
         }
    

    _CULSODA_FILE_NAME = "cuLsoda_all.cu"
    _CULSODA_MAIN_FILE_NAME = "cuLsoda_main.cu"
    
    _KERNEL_NAME = "cuLsoda"
    _INIT_KERNEL_NAME = "init_common"
    _ARGS_TEX_NAME = "args_tex"
    
    _SOURCE_FILE_NAME = "CudaPyInt_generated_code.cu"
    
    def __init__(self, cudaCodePath, constants, compile_options=None):
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
        """
        super(ODESolver, self).__init__()
        self.cudaCodePath = cudaCodePath
        self.constants = constants
        self.compile_options = compile_options
        self.generator = generator.CulsodaCodeGenerator(cudaCodePath, self.constants, self._CULSODA_FILE_NAME, self._CULSODA_MAIN_FILE_NAME, self._ARGS_TEX_NAME)
    
    def _compile(self, write_code):
        """
        Generates and compiles the cuda kernel.
        
        :param write_code: bool
            True if the generated code should be written to the disk
        """
        if self._info:
            print("CudaPyInt: compiling cuda code using {0}").format(self.cudaCodePath)

        options = []
        if(self.compile_options is not None):
            options = options + self.compile_options
            
        code = self.generator.generate(write_code=write_code)
        
        # dummy compile to determine optimal blockSize and gridSize
        sourceModule = self._compileSourceModule(code, options)
        
        blocks, threads = self._getOptimalGPUParam(sourceModule.get_function(self._KERNEL_NAME))
        
        #real compile
        code = self.generator.generate(neq=self._neq, blocks=blocks, threads=threads, write_code=write_code)
        sourceModule = self._compileSourceModule(code, options)
        
        self._d_args = sourceModule.get_texref(self._ARGS_TEX_NAME)
        
        lsodaKernel = sourceModule.get_function(self._KERNEL_NAME)
        
        if self._info:
            print("CudaPyInt: compiling done")
        return (sourceModule, lsodaKernel)
        
    
    def _compileSourceModule(self, code, options):
        """
        Compiles the given code with pycuda using the given options.
        
        :param code: string
            valid CUDA C code to compile
        :param options: list
            List of options passed to the compiler
        """
        return pycuda.compiler.SourceModule(code, nvcc="nvcc", options=options, no_extern_c=True)
    
    def _solve_internal(self, initValues, args, blocks, threads, full_output=False, use_jacobian=False, in_atol=1e-12, in_rtol=1e-6, mxstep=500, h0=0.0):
        """
        Integrates the ODE system for the current blocks. 
        Initializes all required fields on the host and device, executes the gpu computations and returns the integrated values.
        
        :param initValues: array
            Values of y at t0
        :param args: array
            Array of arguments used for the integration.
        :param blocks: int
            Number of threadblocks to launch
        :param threads: int 
            Number of threads to launch per block
        :param full_output: bool (optional)
            True if to return a dictionary of optional infodicts as the second output    
        :param use_jacobian: bool (optional)
            True if a jacobian is provided and should be used for the integration
        :param rtol, atol: float (optional)
            Used for error control
        :param mxstep: integer, (0: solver-determined)
            Maximum number of (internally defined) steps
        :param h0: float, (0: solver-determined)
            The step size to be attempted on the first step.
        """
        
        totalThreads = threads * blocks
        nsystems = len(args)
        
        init_common_Kernel = self._sourceModule.get_function(self._INIT_KERNEL_NAME)
        init_common_Kernel( block=(threads,1,1), grid=(blocks,1) )

        # result array
        results = np.zeros( [totalThreads, self._nresults, self._neq] )
    
        # work spaces of culsoda
        isize = np.int_(20 + self._neq)
        rsize = np.int_(22 + self._neq * max(16, self._neq + 9))
            
        t      = np.zeros( [totalThreads], dtype=np.float64)
        jt     = np.zeros( [1], dtype=np.int32)
        neq    = np.zeros( [1], dtype=np.int32)
        itol   = np.zeros( [1], dtype=np.int32)
        iopt   = np.zeros( [1], dtype=np.int32)
        rtol   = np.zeros( [1], dtype=np.float64)
        tout   = np.zeros( [totalThreads], dtype=np.float64)
        itask  = np.zeros( [1], dtype=np.int32)
        istate = np.zeros( [totalThreads], dtype=np.int32)
        atol   = np.ones( [self._neq], dtype=np.float64)*in_atol
    
        liw    = np.zeros( [1], dtype=np.int32)
        lrw    = np.zeros( [1], dtype=np.int32)
        iwork  = np.zeros( [isize*totalThreads], dtype=np.int32)
        rwork  = np.zeros( [rsize*totalThreads], dtype=np.float64)
        y      = np.zeros( [self._neq*totalThreads], dtype=np.float64)
        
        
        neq[0] = self._neq
        itol[0] = 2
        rtol[0] = in_rtol
        iopt[0] = 0
        liw[0] = isize
        lrw[0] = rsize
        
        if(use_jacobian):
            #1=with jacobian, 2 without
            jt[0] = 1
        else:
            jt[0] = 2
        
        itask[0] = 4
        
        t[0:totalThreads] = self._timepoints[0]
        istate[0:totalThreads] = self.IN_ISTATE_FIRST_CALL
        
        for i in range(totalThreads):
            
            iwork[i*isize+5]=mxstep
            rwork[i*rsize+4]=h0
            rwork[i*rsize+0]=self._timepoints[len(self._timepoints)-1]
            
            try:
            # initial conditions
                for j in range(self._neq):
                    y[i*self._neq + j] = initValues[i][j]
                    results[i, 0, j] = initValues[i][j]
            except IndexError:
                pass
            
        
    
        # copy from host to device
        d_t      = utils.copy_host_to_device(t)
        d_jt     = utils.copy_host_to_device(jt)
        d_neq    = utils.copy_host_to_device(neq)
        d_liw    = utils.copy_host_to_device(liw)
        d_lrw    = utils.copy_host_to_device(lrw)
        d_itol   = utils.copy_host_to_device(itol)
        d_iopt   = utils.copy_host_to_device(iopt)
        d_rtol   = utils.copy_host_to_device(rtol)
        
        d_itask  = utils.copy_host_to_device(itask)
        d_istate = utils.copy_host_to_device(istate)
        d_y      = utils.copy_host_to_device(y)
        d_atol   = utils.copy_host_to_device(atol)
        d_iwork  = utils.copy_host_to_device(iwork)
        d_rwork  = utils.copy_host_to_device(rwork)

        d_isize  = utils.copy_host_to_device(isize)
        d_rsize  = utils.copy_host_to_device(rsize)
        
        d_tout   = driver.mem_alloc(tout.size   * tout.dtype.itemsize)
    
        height = 0
        if(args is not None):
            height, width = args.shape    
            param = np.zeros((totalThreads,width),dtype=np.float32)
            param[0:height]=args[0:height]
            # parameter texture
            ary = utils.create_2D_array(param)
            utils.copy2D_host_to_array(ary, param, width*4, totalThreads )
            self._d_args.set_array(ary)
              
        self._copy_constants()
        
        #prepare infodicts
        infodicts = [[]] * height
        if full_output:
            for i in xrange(height):
                infodicts[i] = {"system": i,
                              "nst":[],
                              "nfe":[],
                              "nje":[],
                          }
        
        #run integrations for every timestep
        for i in range(0,self._nresults):
            tout   = np.ones( [totalThreads], dtype=np.float64)*self._timepoints[i] 
            driver.memcpy_htod( d_tout, tout )
    
            self._compiledKernel( d_neq, d_y, d_t, d_tout, d_itol, d_rtol, d_atol, d_itask, d_istate,
                        d_iopt, d_rwork, d_lrw, d_iwork, d_liw, d_jt, d_isize, d_rsize, block=(threads,1,1), grid=(blocks,1) );

            driver.Context.synchronize()
            driver.memcpy_dtoh(t, d_t)
            driver.memcpy_dtoh(y, d_y)
            driver.memcpy_dtoh(istate, d_istate)
            driver.memcpy_dtoh(iwork, d_iwork)
            
            if full_output:
                for k in xrange(len(args)):
                    infodicts[k]["nst"].append(iwork[k*isize+10])
                    infodicts[k]["nfe"].append(iwork[k*isize+11])
                    infodicts[k]["nje"].append(iwork[k*isize+12])
                    #print "Stop at t=",t[k]," Number of Steps:  ",iwork[k*isize+10], "state is:", istate[k]
    
                #print "---------"
            
            #1=nothing was done, 2 int done
            if(all(istate[0:len(args)]==self.OUT_ISTATE_NOTHING_DONE) or all(istate[0:len(args)]==self.OUT_ISTATE_SUCCESSFULL)):
                for j in range(totalThreads):
                    for k in range(self._neq):
                        results[j, i, k] = y[j*self._neq + k]

            #means an excessive amount of work
            if(any(istate[0:len(args)]==self.OUT_ISTATE_EXCESSIVE_WORK)):
                break

        if full_output:
            for i in xrange(height):
                infodicts[i]["message"] = self._MSGS[istate[i]]
        
        return self._post_process_results(results, infodicts, nsystems, blocks, threads, full_output)
        #return results[0:nsystems], infodicts

    def _post_process_results(self, results, infodicts, nsystems, blocks, threads, full_output):
        """
        Template method to post process the results
        
        :param results: array
            Values of the integrated ODE's
        :param infodicts: array
            Additional infodicts
        :param nsystems: int
            Number of ode systems
        :param blocks: int
            Number of executed blocks
        :param threads: int
            Number of executed threads per block
        :param full_output: bool
            True if additional output is required
        
        """
        return results[0:nsystems], infodicts

    def _copy_constants(self):
        """
        Copies the constants from the host to the device using PyCuda
        """
        for key in self.constants:
            field,_ = self._sourceModule.get_global(key)
            value = self.constants[key]
            
            if(type(value) is float):
                value = np.float_(value)
            elif(type(value) is int):
                value = np.int_(value)
                
            driver.memcpy_htod(field, value)


