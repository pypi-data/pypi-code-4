from dolo.numeric.interpolation.splines import MultivariateSplines
from numpy import *

smin = [-1,-1,-1]
smax = [1,1,1]

orders = [20,20,20]

fun = lambda x: atleast_2d( x.sum(axis=0)**3 )

spline = MultivariateSplines(smin,smax, orders)

values = fun(spline.grid)

spline.set_values(values)



test_interval_1d = atleast_2d( linspace(-2,2,100) )
#test_interval = row_stack( [test_interval_1d*0, test_interval_1d] )



test_interval_0 = row_stack( [test_interval_1d, test_interval_1d*0, test_interval_1d*0] )
test_interval_1 = row_stack( [test_interval_1d*0, test_interval_1d, test_interval_1d*0] )
test_interval_2 = row_stack( [test_interval_1d*0, test_interval_1d*0, test_interval_1d] )

interp_vals_0 = spline(test_interval_0)
interp_vals_1 = spline(test_interval_1)
interp_vals_2 = spline(test_interval_2)

from matplotlib.pylab import *


plot(test_interval_1d.ravel(),interp_vals_0[0,:].ravel(), label='0')
plot(test_interval_1d.ravel(),interp_vals_1[0,:].ravel(), label='1')
plot(test_interval_1d.ravel(),interp_vals_2[0,:].ravel(), label='2')

legend()

show()