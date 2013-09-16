'''
@author: J.Akeret
'''

import numpy as numpy
import sys

sys.path.append("../../")
import cudapyint

def main():
	#determining the timepoints for the output
	a = numpy.logspace(-6,0,1000)
	a_temp = numpy.append(1e-6, a)
	lna = numpy.log(a_temp)
	timepoints = numpy.array(lna,dtype=numpy.float64)
	
	cudaCode = "einstein_boltzmann_ODE.cu"
	
	rec_a=numpy.loadtxt("rec_a_2", numpy.float32)
	rec_xe=numpy.loadtxt("rec_xe_2", numpy.float32)
	ha_a=numpy.loadtxt("ha_a_2", numpy.float32)
	ha_y=numpy.loadtxt("ha_y_2", numpy.float32)
	eta_a=numpy.loadtxt("eta_a_2", numpy.float32)
	
	rec_a = numpy.reshape(rec_a, (len(rec_a),1))
	rec_xe = numpy.reshape(rec_xe, (len(rec_xe),1))
	ha_a = numpy.reshape(ha_a, (len(ha_a),1))
	eta_a = numpy.reshape(eta_a, (len(eta_a),1))
	
	
	lmax = 1
	
	k_sizes = [1]
	for leng in k_sizes:
		k=numpy.array(numpy.logspace(-1,0,leng),dtype=numpy.float32).reshape(leng,1)
		
		y0 = numpy.append(numpy.array([1. , 3./2., 0., 3./2.  , 0  , 1./2. , 0.]), numpy.zeros(2 * lmax - 2))
		
		y0s = numpy.ones([leng,len(y0)], numpy.float32)* y0 * k**(-3./2.)
		
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
		print "Create model..",
		solver = cudapyint.ODESolver(cudaCode, constants)
		print "..calculating.."
		result, info = solver.solve(y0s, timepoints, k, mxstep=1000000, use_jacobian=False, timing=True, info=True, full_output=True, write_code=True)
		print "..finished."
		for d in info:
			print d["system"], d["message"]
			print "nst", d["nst"][-1]
			print "nfe", d["nfe"][-1]
			print "nje", d["nje"][-1]
			
		try:
			import pylab
		except ImportError:
			print "Install pylab to plot the results"
		else:
			y = result[0]
			pylab.figure(num=None, figsize=(11, 12))
			# plot Phi/Phi(0)
			pylab.subplot(3,2,1)
			pylab.title("PyCosmo k=" + str(k[0]) + " lmax="+str(lmax))
			
			pylab.semilogx()
			pylab.plot(a_temp,y[:,0]/y[0,0])
			pylab.xlabel('a')
			pylab.ylabel('Phi/Phi(0)')
			
			pylab.subplot(3,2,3)
			pylab.loglog()
			pylab.plot(a_temp,y[:,3])
			pylab.plot(a_temp,y[:,5])
			pylab.plot(a_temp,y[:,1]*4.)
			pylab.xlabel('a')
			pylab.ylabel('delta_x')
			
			pylab.subplot(3,2,4)
			pylab.semilogx()
			pylab.plot(a_temp,-y[:,4])
			pylab.plot(a_temp,-y[:,6])
			pylab.plot(a_temp,-y[:,2]*3.)
			pylab.xlabel('a')
			pylab.ylabel('-u')
			# plot Theta0
			pylab.subplot(3,2,5)
			pylab.semilogx()
			pylab.plot(a_temp,y[:,5])
			pylab.xlabel('a')
			pylab.ylabel('Theta0')			 
			# plot Theta1
			pylab.subplot(3,2,6)
			pylab.semilogx()
			pylab.plot(a_temp,y[:,6])
			pylab.xlabel('a')
			pylab.ylabel('Theta1')
			pylab.show()

if __name__ == '__main__':
	main()
