import time 
import random
import urllib
import datetime
import numpy as np
import math
from pylab import *

e = 2.71828
pi = 3.14159
global e
global pi

"""SDE key
    u, drift
    s, variability
    dt, time differential
    t, time
    X, current position
    dB, Brownian differential
    B, standard Normal brownian motion
The equation is to be written as a string equation. You will write the equation
that dX is equal to.

ex) u*dt+s*dB"""

#generate a hypothetical economic object
class sim_data:
    def __init__(self, time_max, dt, u, s, init_val, sde):
        self.Xt = []
        self.Bt = []
        self.dBt=[]
        self.dXt = []
        self.time=[]
        t = 0
        B = 0
        X=init_val
        while t<=time_max:
            self.Bt.append(B)
            if s == 0:
                dB = u
            if s>0:
                dB = np.random.normal(u,s)
            self.dBt.append(dB)
            B = B+dB
            self.Xt.append(X)
            dX = eval(sde)
            self.dXt.append(dX)
            X = X+dX
            self.time.append(t)
            t = t + dt
    

#Retrieve Stock data from yahoo finance
"""date in y-m-d, model exp/lin, mode d,w,m daily weekly monthly"""
class stock_data:
    def __init__(self, stock, date1, date2, mode):
        self.date = []
        self.openp = []
        self.high = []
        self.low = []
        self.close = []
        self.volume = []
        self.adjclose = []
        self.perchange = []
        """creates lists for all data downloaded from yahoo finance"""
        byear, bmonth, bday = date1.split("-")
        eyear, emonth, eday = date2.split("-")
        self.mymode=mode
        bmonthminusone = int(bmonth)-1
        bmonthminusone = str(bmonthminusone)
        bday = str(bday)
        byear = str(byear)
        emonthminusone = int(emonth)-1
        emonthminusone = str(emonthminusone)
        eday = str(eday)
        eyear = str(eyear)
        dlurl = 'http://ichart.finance.yahoo.com/table.csv?s='+stock+'&a='+bmonthminusone+'&b='+bday+'&c='+byear+'&d='+emonthminusone+'&e='+eday+'&f='+eyear+'&g='+mode+'&ignore=.csv'
        stockdata = urllib.urlopen(dlurl).read()
        raw = []
        raw = stockdata.split('\n')
        raw = [a.replace(",", "::") for a in raw]
        for a in raw:
            cool = a.split("::")
            if len(cool)>5:
                self.adjclose.append(cool.pop())
                self.volume.append(cool.pop())
                self.close.append(cool.pop())
                self.low.append(cool.pop())
                self.high.append(cool.pop())
                self.openp.append(cool.pop())
                self.date.append(cool.pop())
        self.date.remove('Date')
        self.openp.remove('Open')
        self.high.remove('High')
        self.low.remove('Low')
        self.close.remove('Close')
        self.volume.remove('Volume')
        self.adjclose.remove('Adj Close')
        self.openp = [float(a) for a in self.openp]
        self.high =[float(a) for a in self.high]
        self.low =[float(a) for a in self.low]
        self.close =[float(a) for a in self.close]
        self.volume =[float(a) for a in self.volume]
        self.adjclose = [float(a) for a in self.adjclose]

#generate model of stock values, including historic drift and volatility
    def gen_model(self, model):
        if model=='exp':
            self.perchange = [(b-a)/a for a,b in zip(self.close,self.openp)]
        if model=='lin':
            self.perchange = [(b-a) for a,b in zip(self.close,self.openp)]
        self.drift = sum(self.perchange)/(len(self.perchange))
        variance = sum([(a-self.drift)**2 for a in self.perchange])/(len(self.perchange))
        self.std = np.sqrt(variance)
        step = 1
        y = self.close[len(self.close)-1]
        self.model=[y]
        while step<len(self.date):
            #k=random.gauss(self.drift, self.std)
            if model=='lin':
                k=self.drift
            #k = (self.drift*y)+(self.std*y*self.dWt())
            if model=='exp':
                k = (self.drift*y)
            y = y+k
            self.model.append(y)
            step = step+1
        self.model.reverse()


#Probability on the normal model from a to b
def P(a,b):
    x = a
    dx = .05
    dy = []
    while x<=b:
        yprime = (1/sqrt(2*pi))*(e**(-.5*(x**2)))
        dy.append(yprime*dx)
        x = x+dx
    return sum(dy)

#N'(x), evaluating the normal model at a given x
def M(x):
    return (1/sqrt(2*pi))*(e**(-.5*(x**2)))


#calculate call option value
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def put(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    d2 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r-(v**2)/2)*tm)
    c =  P(-10, -d2)*K*e**(-r*tm)-P(-10, -d1)*S
    return c


#calculate call option value
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def call(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    d2 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r-(v**2)/2)*tm)
    c = P(-10, d1)*S - P(-10, d2)*K*e**(-r*tm)
    return c

#calculate call option delta
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def Call_delta(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    m = P(-10, d1)
    return m

#calculate call option gamma
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def Call_Gamma(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    k = M(d1)*(1/(S*v*sqrt(tm)))
    return k

#calculate call option Theta
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def Call_Theta(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    d2 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r-(v**2)/2)*tm)
    k = (-S*M(d1)*v)*(1/(2*sqrt(tm)))-P(-10,d2)*r*K*e**(-r*tm)
    return k

#calculate put option delta
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def Put_delta(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    m = P(-10, d1)-1
    return m

#Calculate put option Gamma
#same as Call option Gamma
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def Put_Gamma(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    k = M(d1)*(1/(S*v*sqrt(tm)))
    return k

#Calculate put option Theta
#input (time to maturity, Stock value, Strike, interest rate, volatility)
def Put_Theta(tm, S, K, r, v):
    d1 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r+(v**2)/2)*tm)
    d2 = (1/(v*sqrt(tm)))*(math.log(S/K, e)+(r-(v**2)/2)*tm)
    k = (-S*M(d1)*v)*(1/(2*sqrt(tm)))+P(-10,-d2)*r*K*e**(-r*tm)
    return k


