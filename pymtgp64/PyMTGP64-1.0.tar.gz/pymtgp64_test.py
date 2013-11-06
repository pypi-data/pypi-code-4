#! /usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import pymtgp64
import time

# initialisation:

block = 192
device = 0

n= int( 1e7 )

# initial seed value (an arbitray number ... my birthday)
seed= 31121971 

# initialization of the module
seeds = pymtgp64.init(seed,device=device,block=block)

print ("device: %d , number of block: %d") % ( pymtgp64.device(),pymtgp64.block_num()) 


# uniform distributions
print '-----------------------'
print 'uniform distributions'
print 'host calculation:'
t1 = time.time() 
x = np.random.uniform(low=0.,high=1.,size=n)
print 'duration (s): ',time.time()-t1
print 'mean, median, stddev, min, max, max-1.'
print ("%f, %f, %f, %e, %e, %e") % (np.mean(x) , np.median(x), np.std(x),  np.min(x), np.max(x) ,  np.max(x)-1. )

print 'gpu calculation:'
t1 = time.time()
x = pymtgp64.uniform(n)
print 'duration (s): ',time.time()-t1
print 'mean, median, stddev, min, max, max-1.'
print ("%f, %f, %f, %e, %e, %e") % (np.mean(x) ,  np.median(x), np.std(x),  np.min(x), np.max(x) , np.max(x)-1. )

plt.figure(0)
plt.clf()
plt.hist(x,bins=100)

print ''
print '-----------------------'
print 'Normal distributions'

print 'host calculation:'
t1 = time.time()      
x = np.random.normal(0.,1.,size=n)
y = np.random.normal(0.,1.,size=n)
print 'duration (s): ',time.time()-t1
print 'mean, median, stddev, min, max'
print ("%f, %f, %f, %e, %e") % (np.mean(x) ,  np.median(x), np.std(x),  np.min(x), np.max(x)  )


print 'gpu calculation:'
t1 = time.time()
(x,y) = pymtgp64.normal(n)
print 'duration (s): ',time.time()-t1
print 'mean, median, stddev, min, max'
print ("%f, %f, %f, %e, %e") % (np.mean(x) ,  np.median(x), np.std(x),  np.min(x), np.max(x)  )
plt.figure(1)
plt.clf()
plt.hist(x,bins=100)

print ''
print '-----------------------'
print 'Poisson distribution'
print 'host calculation:'
lam= 12. # the mean value of the distribution ('lambda' parameter)
t1 = time.time()
x = np.random.poisson(lam=lam,size=n)
print 'duration (s): ',time.time()-t1
print 'mean, median, stddev, min, max'
print ("%f, %f, %f, %e, %e") % (np.mean(x) , np.median(x), np.std(x),  np.min(x), np.max(x))

print 'gpu calculation:'
t1 = time.time()
x = pymtgp64.poisson(lam,n)
print 'duration (s): ',time.time()-t1
print 'mean, median, stddev, min, max'
print ("%f, %f, %f, %e, %e") % (np.mean(x) ,  np.median(x), np.std(x),  np.min(x), np.max(x))

plt.figure(2)
plt.hist(x,bins=100)

print ''
print '-----------------------'
print 'Poisson distribution with mutliple lambda values'
n = 1e5
lam =  np.random.uniform(low=1.,high=1e5,size=n)  # in this test case we generate random values of 'lambda'
print 'host calculation:'
t1 = time.time()
x = np.zeros(n)
for i in range(n):
    x[i]  = np.random.poisson(lam=lam[i],size=1)
print 'duration (s): ',time.time()-t1

print 'gpu calculation:'
t1 = time.time()
x = pymtgp64.poisson_multlam(lam)
print 'duration (s): ',time.time()-t1


# we free the memory used by the module
pymtgp64.free()

plt.show()

