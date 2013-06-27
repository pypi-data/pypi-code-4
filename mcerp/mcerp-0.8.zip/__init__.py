# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:48:17 2013

@author: Abraham Lee
"""
from ad import ADF,ADV
import numpy as np
import math
from lhd import lhd
import scipy.stats as ss
import matplotlib.pyplot as plt

__all__ = ['uv']

npts = 10000

CONSTANT_TYPES = (float,int,complex,long,np.number)

class NotUpcast(Exception):
    'Raised when an object cannot be converted to a number with uncertainty'

def to_uncertain_func(x):
    """
    Transforms x into a constant automatically differentiated function (ADF),
    unless it is already an ADF (in which case x is returned unchanged).

    Raises an exception unless 'x' belongs to some specific classes of
    objects that are known not to depend on AffineScalarFunc objects
    (which then cannot be considered as constants).
    """
#    print 'to_uncertain_func:',x.__class__
#    print "hasattr(x,'_mcpts'):",hasattr(x,'_mcpts')
#    if isinstance(x, UncertainFunction):
    if hasattr(x,'_mcpts'):
        return x

    #! In Python 2.6+, numbers.Number could be used instead, here:
    elif isinstance(x, CONSTANT_TYPES):
        # No variable => no derivative to define:
        return UncertainFunction(x, {}, {}, {}, x)
    
    raise NotUpcast("%s cannot be converted to a number with"
                    " uncertainty" % type(x))
    
    

class UncertainFunction(ADF):
    """
    UncertainFunction objects represent the uncertainty of a result of 
    calculations with uncertain variables. Nearly all basic mathematical
    operations are supported.
    
    This class is mostly intended for internal use.
    
    
    """
    def __init__(self,x,d,d2,d2c,mcpts):
        self._mcpts = np.atleast_1d(mcpts)
        ADF.__init__(self,x,d,d2,d2c)

#    @property
    def mean(self):
        """
        Mean value as a result of an uncertainty calculation
        """
        mn = np.mean(self._mcpts)
        return mn
    
    def var(self):
        """
        Variance value as a result of an uncertainty calculation
        """
        mn = self.mean()
        vr = np.mean((self._mcpts-mn)**2)
        return vr
        
#    @property
    def std(self):
        """
        Standard deviation value as a result of an uncertainty calculation, 
        defined as::
            
                    ________
            std = \/variance
            
        """
        return self.var()**0.5
    
#    @property
    def skew(self):
        """
        Skewness coefficient value as a result of an uncertainty calculation,
        defined as::
            
              _____     m3
            \/beta1 = ------
                      std**3
        
        where m3 is the third central moment and std is the standard deviation
        """
        mn = self.mean()
        sd = self.std()
        sk = 0.0 if abs(sd)<=1e-8 else np.mean((self._mcpts-mn)**3)/sd**3
        return sk
    
#    @property
    def kurt(self):
        """
        Kurtosis coefficient value as a result of an uncertainty calculation,
        defined as::
            
                      m4
            beta2 = ------
                    std**4

        where m4 is the fourth central moment and std is the standard deviation
        """
        mn = self.mean()
        sd = self.std()
        kt = 0.0 if abs(sd)<=1e-8 else np.mean((self._mcpts-mn)**4)/sd**4
        return kt
    
#    @property
    def stats(self):
        """
        The first four standard moments of a distribution: mean, variance, and
        standardized skewness and kurtosis coefficients.
        """
        mn = self.mean()
        vr = self.var()
        sk = self.skew()
        kt = self.kurt()
        return [mn,vr,sk,kt]
        
    
    def __str__(self):
        mn,vr,sk,kt = self.stats()
        s = 'UncertainFunction:\n'
        s += ' > Mean................... {: }\n'.format(mn)
        s += ' > Variance............... {: }\n'.format(vr)
        s += ' > Skewness Coefficient... {: }\n'.format(sk)
        s += ' > Kurtosis Coefficient... {: }'.format(kt)
        return s

    def __repr__(self):
        return 'UF({:}, {:}, {:}, {:})'.format(*self.stats())

    def plot(self,**kwargs):
        vals = self._mcpts
        low = min(vals)
        high = max(vals)

#        p = ss.kde.gaussian_kde(vals)
#        xp = np.linspace(low,high,100)

        plt.figure()
#        plt.plot(xp,p.evaluate(xp))
        plt.hist(vals,bins=np.round(np.sqrt(npts)),histtype='stepfilled')
        plt.title(repr(self))
        plt.xlim(low-(high-low)*0.1,high+(high-low)*0.1)
        plt.ylim(ymin=0)
        plt.show()

    def __add__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts + uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__add__(self,val),mcpts)

    def __radd__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts + uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__radd__(self,val),mcpts)
        
    def __mul__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts * uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__mul__(self,val),mcpts)

    def __rmul__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts * uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__rmul__(self,val),mcpts)
        
    def __sub__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts - uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__sub__(self,val),mcpts)

    def __rsub__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[1]._mcpts - uf[0]._mcpts
        return _make_UF_compatible_object(ADF.__rsub__(self,val),mcpts)
        
    def __div__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts/uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__div__(self,val),mcpts)

    def __rdiv__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[1]._mcpts/uf[0]._mcpts
        return _make_UF_compatible_object(ADF.__rdiv__(self,val),mcpts)
        
    def __truediv__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts/uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__truediv__(self,val),mcpts)

    def __rtruediv__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[1]._mcpts/uf[0]._mcpts
        return _make_UF_compatible_object(ADF.__rtruediv__(self,val),mcpts)
        
    def __pow__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[0]._mcpts**uf[1]._mcpts
        return _make_UF_compatible_object(ADF.__pow__(self,val),mcpts)

    def __rpow__(self,val):
        uf = map(to_uncertain_func,[self,val])
        mcpts = uf[1]._mcpts**uf[0]._mcpts
        return _make_UF_compatible_object(ADF.__rpow__(self,val),mcpts)
    
    def __neg__(self):
        mcpts = -self._mcpts
        return _make_UF_compatible_object(ADF.__neg__(self),mcpts)
        
    def __pos__(self):
        mcpts = self._mcpts
        return _make_UF_compatible_object(ADF.__pos__(self),mcpts)
    
    def __abs__(self):
        mcpts = np.abs(self._mcpts)
        return _make_UF_compatible_object(ADF.__abs__(self),mcpts)
    
    def __eq__(self,val):
        diff = self-val
        return not (diff.mean() or diff.var() or diff.skew() or diff.kurt())
    
    def __ne__(self,val):
        return not self==val
    
    def __lt__(self,val):
        self,val = map(to_uncertain_func,[self,val])
        return True if float(self.mean()-val.mean()) < 0 else False
    
    def __le__(self,val):
        return (self==val) or self < val
    
    def __gt__(self,val):
        return not self < val
    
    def __ge__(self,val):
        return (self==val) or self > val

    def __nonzero__(self):
        return self!=0

def _make_UF_compatible_object(tmp,mcpts):
    if isinstance(tmp,ADF):
        return UncertainFunction(tmp.x,tmp.d(),tmp.d2(),tmp.d2c(),mcpts)
    else: # for scalars, etc.
        return UncertainFunction(tmp,{},{},{},[tmp]*npts)

################################################################################

class UncertainVariable(UncertainFunction,ADV):
    """
    UncertainVariable objects track the effects of uncertainty, characterized 
    in terms of the first four standard moments of statistical distributions 
    (mean, variance, skewness and kurtosis coefficients). Monte Carlo simulation,
    in conjunction with Latin-hypercube based sampling performs the calculations.

    Parameters
    ----------
    rv : scipy.stats.distribution
        A distribution to characterize the uncertainty
    
    tag : str, optional
        A string identifier when information about this variable is printed to
        the screen
        
    Notes
    -----
    
    The ``scipy.stats`` module contains many distributions which we can use to
    perform any necessary uncertainty calculation. It is important to follow
    the initialization syntax for creating any kind of distribution object:
        
        - *Location* and *Scale* values must use the kwargs ``loc`` and 
          ``scale``
        - *Shape* values are passed in as non-keyword arguments before the 
          location and scale, (see below for syntax examples)..
        
    The mathematical operations that can be performed on uncertain objects will 
    work for any distribution supplied, but may be misleading if the supplied 
    moments or distribution is not accurately defined. Here are some guidelines 
    for creating UncertainVariable objects using some of the most common 
    statistical distributions:
        
    =========================  ==============  ==================  ============  ============
    Distribution               scipy.stats     args                loc           scale
                               class name      (shape parameters)
    =========================  ==============  ==================  ============  ============
    Normal(mu,sigma)           norm                                mu            sigma
    Uniform(a,b)               uniform                             a             b-a
    Exponential(lambda)        expon                                             1/lambda
    Gamma(k,theta)             gamma           k                                 theta
    Beta(alpha,beta,[a,b])     beta            alpha,beta          a             b-a
    Log-Normal(mu,sigma)       lognorm         sigma               mu
    Chi-Square(dv)             chi2            dv
    F(df_numer,df_denom)       f               df_numer,df_denom
    Triangular(a,b,peak)       triang          peak                a             b-a
    Student-T(df)              t               df
    =========================  ==============  ==================  ============  ============
    
    Thus, each distribution above would have the same call signature::
        
        >>> import scipy.stats as ss
        >>> ss.your_dist_here(args,loc=loc,scale=scale)
        
    Examples
    --------
    A three-part assembly
        
        >>> import scipy.stats as ss
        >>> x1 = uv(ss.norm(loc=24,scale=1)) # normally distributed
        >>> x2 = uv(ss.norm(loc=37,scale=4)) # normally distributed
        >>> x3 = uv(ss.expon(scale=0.5))     # exponentially distributed
        >>> Z = (x1*x2**2)/(15*(1.5+x3))
        >>> Z
        UF(1161.46231679, 116646.762981, 0.345533974771, 3.00791101068)

    The result shows the mean, variance, and standardized skewness and kurtosis
    of the output variable Z, which will vary from use to use due to the random
    nature of Monte Carlo simulation and latin-hypercube sampling techniques.
    
    Basic math operations may be applied to distributions, where all 
    statistical calculations are performed using latin-hypercube enhanced Monte
    Carlo simulation. Nearly all of the built-in trigonometric-, logarithm-, 
    etc. functions of the ``math`` module have uncertainty-compatible 
    counterparts that should be used when possible since they support both 
    scalar values and uncertain objects. These can be used after importing the 
    ``umath`` module::
        
        >>> from mcerp.umath import * # sin(), sqrt(), etc.
        >>> sqrt(x1)
        UF(4.89791765647, 0.0104291897681, -0.0614940614672, 3.00264937735)
    
    At any time, the standardized statistics can be retrieved using::
        
        >>> x1.stats()
        [24.0, 1.0, 0.0, 3.0]
    
    By default, the Monte Carlo simulation uses 10000 samples, but this can be
    changed at any time with::
        
        >>> mcerp.npts = number_of_samples
    
    Any value from 1,000 to 1,000,000 is recommended (more samples means more
    accurate, but also means more time required to perform the calculations). 
    Although it can be changed, since variables retain their samples from one
    calculation to the next, this parameter should be changed before any 
    calculations are performed to ensure parameter compatibility (this may 
    change to be more dynamic in the future, but for now this is how it is).
    
    Also, to see the underlying distribution of the variable, and if matplotlib
    is installed, simply call its plot method::
        
        >>> x1.plot()
    
    Optional kwargs can be any valid kwarg used by matplotlib.pyplot.plot
        
    """
    
    def __init__(self,rv,tag=None):
        assert hasattr(rv,'dist'), 'Keyword "rv" must be a distribution from the scipy.stats module.'

        self.rv = rv
        
        # generate the latin-hypercube points
        self._mcpts = lhd(dist=self.rv,size=npts)
        
        ADV.__init__(self,self.rv.mean(),tag=tag)
    
#    @property
    def mean(self):
        return float(self.rv.stats('m'))
    
#    @property
    def var(self):
        return float(self.rv.stats('v'))
		
#    @property
    def std(self):
        return self.var()**0.5
        
#    @property
    def skew(self):
        return float(self.rv.stats('s'))
    
#    @property
    def kurt(self):
        return float(self.rv.stats('k'))+3
    
#    @property
    def stats(self):
        return [self.mean(),self.var(),self.skew(),self.kurt()]
    
    def __str__(self):
        if self.tag:
            s = 'UncertainVariable ('+self.tag+'):\n'
        else:
            s = 'UncertainVariable:\n'
        s += ' > Mean................... {: }\n'.format(self.mean())
        s += ' > Variance............... {: }\n'.format(self.var())
        s += ' > Skewness Coefficient... {: }\n'.format(self.skew())
        s += ' > Kurtosis Coefficient... {: }'.format(self.kurt())
        return s

    def __repr__(self):
        if self.tag:
            name = self.tag
        elif self.rv is not None:
            name = self.rv.dist.name
        else:
            name = 'UV'
        return name+'({:}, {:}, {:}, {:})'.format(*self.stats())

    def plot(self,vals=None,**kwargs):
        """
        Plot the distribution of the UncertainVariable.
        
        Optional
        --------
        vals : array-like
            If no values are put in, default x-values between the 0.01% and 
            99.99% points will be used.
        
        kwargs : any valid matplotlib.pyplot.plot kwarg
        
        """
        if vals is None:
            low = self.rv.ppf(0.0001)
            high = self.rv.ppf(0.9999)
            vals = np.linspace(low,high,500)
        else:
            low = min(vals)
            high = max(vals)

        plt.plot(vals,self.rv.pdf(vals),**kwargs)
        plt.title(repr(self))
        plt.xlim(low-(high-low)*0.1,high+(high-low)*0.1)
        plt.show()
                
        
uv = UncertainVariable # a nicer form for the user

if __name__=='__main__':
    
    import mcerp.umath as umath
    
    print '*'*80
    print 'SAME TEST FUNCTIONS USING DERIVED MOMENTS FROM SCIPY DISTRIBUTIONS'
    print '*'*80
    print 'Example of a three part assembly'
    x1 = uv(ss.norm(loc=24,scale=1))   # normally distributed
    x2 = uv(ss.norm(loc=37,scale=4))   # normally distributed
    x3 = uv(ss.expon(scale=0.5))       # exponentially distributed
    
    Z = (x1*x2**2)/(15*(1.5+x3))
    print Z
#    Z.plot()
    
    print '*'*80
    print 'Example of volumetric gas flow through orifice meter'
    H = uv(ss.norm(loc=64,scale=0.5))
    M = uv(ss.norm(loc=16,scale=0.1))
    P = uv(ss.norm(loc=361,scale=2))
    t = uv(ss.norm(loc=165,scale=0.5))
    C = 38.4
    Q = C*umath.sqrt((520*H*P)/(M*(t+460)))
    print Q
#    Q.plot()

    print '*'*80
    print 'Example of manufacturing tolerance stackup'
    # for a gamma distribution we need the following conversions:
    # scale = var/mean
    # shape = mean**2/var
    mn = 1.5
    vr = 0.25
    scale = vr/mn
    shape = mn**2/vr
    x = uv(ss.gamma(shape,scale=scale)) 
    y = uv(ss.gamma(shape,scale=scale)) 
    z = uv(ss.gamma(shape,scale=scale))
    w = x+y+z
    print w
#    w.plot()

    print '*'*80
    print 'Example of scheduling facilities (six stations)'
    s1 = uv(ss.norm(loc=10,scale=1))
    s2 = uv(ss.norm(loc=20,scale=2**0.5))
    mn1 = 1.5
    vr1 = 0.25
    scale1 = vr1/mn1
    shape1 = mn1**2/vr1
    s3 = uv(ss.gamma(shape1,scale=scale1))
    mn2 = 10
    vr2 = 10
    scale2 = vr2/mn2
    shape2 = mn2**2/vr2
    s4 = uv(ss.gamma(shape2,scale=scale2))
    s5 = uv(ss.expon(scale=0.2))
    s6 = uv(ss.chi2(10))
    T = s1+s2+s3+s4+s5+s6
    print T
#    T.plot()

    print '*'*80
    print 'Example of two-bar truss'
    H = uv(ss.norm(loc=30,scale=5/3.),tag='H')
    B = uv(ss.norm(loc=60,scale=0.5/3.),tag='B')
    d = uv(ss.norm(loc=3,scale=0.1/3),tag='d')
    t = uv(ss.norm(loc=0.15,scale=0.01/3),tag='t')
    E = uv(ss.norm(loc=30000,scale=1500/3.),tag='E')
    rho = uv(ss.norm(loc=0.3,scale=0.01/3.),tag='rho')
    P = uv(ss.norm(loc=66,scale=3/3.),tag='P')
    pi = math.pi
    wght = 2*pi*rho*d*t*umath.sqrt((B/2)**2+H**2)
    strs = (P*umath.sqrt((B/2)**2+H**2))/(2*pi*d*t*H)
    buck = (pi**2*E*(d**2+t**2))/(8*((B/2)**2+H**2))
    defl = (P*((B/2)**2+H**2)**(1.5))/(2*pi*d*t*H**2*E)
    print 'wght:',wght
    print 'strs:',strs
    print 'buck:',buck
    print 'defl:',defl
#    wght.plot()
#    strs.plot()
#    buck.plot()
#    defl.plot()
##    wght.error_components(pprint=True)
