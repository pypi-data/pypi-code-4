'''
@author: J.Akeret
'''

import numpy as numpy
import time

import sys
sys.path.append("../../")
import cudapyint

def run_benchmarks(constants, timepoints, k_size, lmax=1, mem="global", use_jacobian=False, parallel=False, threads=1):
    
    k=numpy.array(numpy.logspace(-1,0,k_size),dtype=numpy.float32).reshape(k_size,1)
    
    y0 = numpy.append(numpy.array([1. , 3./2., 0., 3./2.  , 0  , 1./2. , 0.]), numpy.zeros(2 * lmax - 2))
    
    y0s = numpy.ones([k_size,len(y0)], numpy.float32)* y0 * k**(-3./2.)

    if(mem=="global"):
        if(parallel==False):
            cudaCode = "../../examples/einsteinboltzmann/einstein_boltzmann_ODE.cu"
            solver = cudapyint.ODESolver(cudaCode, constants)
        else:
            cudaCode = "../../examples/einsteinboltzmann/einstein_boltzmann_ODE_parallel.cu"
            solver = cudapyint.ParallelODESolver(cudaCode, constants, threads=threads)
            
    elif(mem=="shared"):
        if(parallel==False):
            cudaCode = "../../examples/einsteinboltzmann/einstein_boltzmann_ODE.cu"
            solver = cudapyint.ODESolverSharedMemory(cudaCode, constants)
        else:
            cudaCode = "../../examples/einsteinboltzmann/einstein_boltzmann_ODE_parallel.cu"
            solver = cudapyint.ParallelODESolverSharedMemory(cudaCode, constants, threads=threads)
    
    start = time.time()
    result = solver.solve(y0s, timepoints, k, mxstep=1000000, use_jacobian=use_jacobian, timing=True, info=True, write_code=False)
    print result
    end = time.time()
    print("lmax: {0}\t mem: {1}\t use_jacobian: {2}\t parallel: {3}\t k_size: {4}\t time\t {5}").format(lmax, mem, use_jacobian, parallel, k_size, round((end - start), 4))
    

print("Recieved args: {0}").format(sys.argv)
if(len(sys.argv)<3):
    print("missing args. expected: mem model, with_jacobian, [lmax], [k]")
    exit(0)

mem_models = ["global", "shared"]
if(sys.argv[1] in mem_models):
    mem_model = sys.argv[1]
else:
    exit(0)

with_jac = "True" == sys.argv[2]

if(len(sys.argv)>=4):
    lmax = int(sys.argv[3])
else:
    lmax = 1

if(len(sys.argv)>=5):
    k_sizes = [int(sys.argv[4])]
else:
    k_sizes = [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,20000,30000,40000,50000,60000,70000,80000,90000,100000]

a = [1.0]
a_temp = numpy.append(1e-6, a)
lna = numpy.log(a_temp)
timepoints = numpy.array(lna,dtype=numpy.float64)

rec_a=numpy.loadtxt("rec_a", numpy.float32)
rec_xe=numpy.loadtxt("rec_xe", numpy.float32)
ha_a=numpy.loadtxt("ha_a", numpy.float32)
ha_y=numpy.loadtxt("ha_y", numpy.float32)
eta_a=numpy.loadtxt("eta_a", numpy.float32)

rec_a = numpy.reshape(rec_a, (len(rec_a),1))
rec_xe = numpy.reshape(rec_xe, (len(rec_xe),1))
ha_a = numpy.reshape(ha_a, (len(ha_a),1))
eta_a = numpy.reshape(eta_a, (len(eta_a),1))

constants = {
    "h": 0.7,
    "rh": 2997.9245799999994,
    "omega_gam": 5.040816326530613e-05, 
    "omega_r": 8.475235150739534e-05,
    "omega_b": 0.045,
    "omega_dm": 0.255,
    "rec_a": rec_a,
    "rec_xe": rec_xe,
    "ha_a": ha_a, 
    "ha_y": ha_y, 
    "eta_a":eta_a,
    }

print("a: {0}\t len constants: {1}").format(timepoints, len(ha_a))

for k_size in k_sizes:
    run_benchmarks(constants, timepoints, k_size, lmax, mem_model, with_jac);
