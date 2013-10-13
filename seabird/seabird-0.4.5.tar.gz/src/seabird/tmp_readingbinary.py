fp = open("at017094.cnv")
content = fp.read()
header, data = content.split('*END*\r\n', 1)
from numpy import fromstring
data = fromstring(data, 'f')
data.reshape(33927,10)[:,0] # Shows the timeseries of the first variable.


data.shape = (-1, nquan)
