from pandas.io.data import get_data_yahoo
import matplotlib.pyplot as plt
 
data = get_data_yahoo("AAPL", start = '2012-01-01', end = '2012-12-31')[['Close', 'Volume']]
data.plot(subplots = True, figsize = (8, 8));
plt.legend(loc = 'best')
plt.show()
