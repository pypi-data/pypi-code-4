
from numpy import linspace, random

from lmfit import Parameters, minimize, conf_interval, report_errors, report_ci


def residual(pars, x, data):
    m = pars['m'].value
    c = pars['c'].value

    return data -  (m*x + c)

npts  = 2500

noise = random.normal(scale=5.00, size=npts)
x     = linspace(0, 100,  npts)
data  = 15* x -33.0 + noise

fit_params = Parameters()
fit_params.add('c', value=5.0)
fit_params.add('m', value=21)

result = minimize(residual, fit_params, args=(x,data))

fit = residual(fit_params, x, data)

print '#- Error Report from minimize():'
report_errors(fit_params)

print 'Success: ', result.success
print '#- Confidence Intervals:'
ci, tr = conf_interval(result, trace=True, verbose=1)
report_ci(ci)
print '#--'
    

