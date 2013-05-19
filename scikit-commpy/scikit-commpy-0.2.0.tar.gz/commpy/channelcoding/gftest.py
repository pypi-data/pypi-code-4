from galoisfields import *
import numpy as np

m = 4
n = np.arange(16)
#print type(n) is list

x = gf(n, m)

y = gf(7, 4)

print 'Polynomial:'

p = primpoly(m)
print p
print x.elements
coset_obj_array = cosets(m)

for i in range(len(coset_obj_array)):
    print coset_obj_array[i].elements

print power2tuple(9, m)

print polymultiply(10, p, m)
prod_obj = x*y
print prod_obj.elements


#print y
print minpol(x)

#print p
#z = x + y
#z = x*
#print z.elementi
