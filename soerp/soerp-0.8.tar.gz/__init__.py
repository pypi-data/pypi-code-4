# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:48:17 2013

@author: tisimst
"""
import ad
from ad import ADF,ADV
from method_of_moments import soerp_numeric,variance_components,variance_contrib
import numpy as np
import math
import sys

__all__ = ['uv', 'raw2central']

CONSTANT_TYPES = (float,int,complex,long,np.number)

def to_uncertain_func(x):
    """
    Transforms x into a constant automatically differentiated function (ADF),
    unless it is already an ADF (in which case x is returned unchanged).

    Raises an exception unless 'x' belongs to some specific classes of
    objects that are known not to depend on AffineScalarFunc objects
    (which then cannot be considered as constants).
    """

    if isinstance(x, UncertainFunction):
        return x

    #! In Python 2.6+, numbers.Number could be used instead, here:
    if isinstance(x, CONSTANT_TYPES):
        # No variable => no derivative to define:
        return UncertainFunction(x, {}, {}, {})

class UncertainFunction(ADF):
    """
    UncertainFunction objects represent the uncertainty of a result of 
    calculations with uncertain variables. Nearly all basic mathematical
    operations are supported.
    
    This class is mostly intended for internal use.
    
    
    """
#    def __init__(self,*args,**kwargs):
#        ADF.__init__(self,*args,**kwargs)

#    @property
    def mean(self):
        """
        Mean value as a result of an uncertainty calculation
        """
        mn,vr,sk,kt = self.moments()
        return mn
    
    def var(self):
        """
        Variance value as a result of an uncertainty calculation
        """
        mn,vr,sk,kt = self.moments()
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
        mn,vr,sk,kt = self.moments()
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
        mn,vr,sk,kt = self.moments()
        return kt
    
#    @property
    def moments(self):
        """
        The first four standard moments of a distribution: mean, variance, and
        standardized skewness and kurtosis coefficients.
        """
        slc,sqc,scp,var_moments,f0 = self._get_inputs_for_soerp()
        mn,vr,sk,kt = soerp_numeric(slc,sqc,scp,var_moments,f0,silent=True)
        return [mn,vr,sk,kt]
        
    def error_components(self, pprint=False, as_eq_terms=False):
        """
        The parts of the second order approximation of the variance function,
        returned in three pieces if ``as_eq_terms`` = True, first-order 
        components, pure-quadratic components, and cross-product components,
        otherwise the error components from the linear terms are added to the 
        corresponding error components from the quadratic terms. Any 
        cross-product term components are divided equally between the two 
        factors of the cross-product.
        
        Optional
        --------
        pprint : bool, default is False,
            Pretty-print the error components, showing both the component and
            the percent contribution of the component
        as_eq_terms : bool, default is False,
            True to return the error components in the form of the equation 
            terms (pure linear, pure quadratic, and cross-product), where both
            orders are available for the cross-product terms (i.e., (x, y) and 
            (y, x) will be returned in the cross-product terms), otherwise in 
            terms of the contributing UncertainVariables.
        
        Returns
        -------
        err_comp : dict
            A dictionary (or three if ``as_eq_terms`` = True) that maps the 
            error components to the contributing UncertainVariables.
            
        Example
        --------
        If we had a function of two variables ended up with the linear terms 
        (``as_eq_terms`` = False here), ::
            
            >>> lc = {x:0.5, y:0.25}
        
        the quadratic terms::
            
            >>> qc = {x:0.2, y:0.1}
        
        and the cross-product term::
            
            >>> cp = {(x, y}:0.14}
        
        then the variables would be given the error components like this::
            
            >>> lc[x] + qc[x] + 0.5*cp[(x, y)] # first variable, x
            0.77
            >>> lc[y] + qc[y] + 0.5*cp[(x, y)] # second variable, y
            0.42
            
        """
        variables = self.d().keys()
        slc,sqc,scp,var_moments,f0 = self._get_inputs_for_soerp()
        vz = self.moments()
        vz[2] = vz[2]*vz[1]**1.5 #convert back to central moments
        vz[3] = vz[3]*vz[1]**2
        vz = [1]+vz
        vlc,vqc,vcp = variance_components(slc,sqc,scp,var_moments,vz)
        
        vc_lc = {}
        vc_qc = {}
        vc_cp = {}
        
        for i,v1 in enumerate(variables):
            vc_lc[v1] = vlc[i]
            vc_qc[v1] = vqc[i]
            for j,v2 in enumerate(variables):
                if i<j:
                    vc_cp[(v1,v2)] = vcp[i,j]
                    vc_cp[(v2,v1)] = vcp[i,j]
        
        if not as_eq_terms:
            error_wrt_var = dict((v, 0.) for v in variables)
            for i,v1 in enumerate(variables):
                if vc_lc.has_key(v1):
                    error_wrt_var[v1] += vc_lc[v1]
                    error_wrt_var[v1] += vc_qc[v1]
                for j,v2 in enumerate(variables):
                    if i<j:
                        if vc_cp.has_key((v1,v2)):
                            error_wrt_var[v1] += 0.5*vc_cp[(v1,v2)]
                            error_wrt_var[v2] += 0.5*vc_cp[(v1,v2)]
            if pprint:
                print '*'*65
                print 'COMPOSITE VARIABLE ERROR COMPONENTS'
                for v in variables:
                    print '{:} = {:} or {:%}'.format(v.__repr__(),error_wrt_var[v],np.abs(error_wrt_var[v]/vz[2]))
            
            return error_wrt_var
        else:
            if pprint:
                vcont_lc,vcont_qc,vcont_cp = variance_contrib(vlc,vqc,vcp,vz)
                print '*'*65
                print 'Linear error components:'
                for i,v1 in enumerate(variables):
                    if vc_lc.has_key(v1):
                        print '{:} = {:} or {:%}'.format(v1.__repr__(),vc_lc[v1],vcont_lc[i])
                    else:
                        print '{:} = {:} or {:%}'.format(v1.__repr__(),0.0,0.0)
                
                print '*'*65
                print 'Quadratic error components:'
                for i,v1 in enumerate(variables):
                    if vc_qc.has_key(v1):
                        print '{:} = {:} or {:%}'.format(v1.__repr__(),vc_qc[v1],vcont_qc[i])
                    else:
                        print '{:} = {:} or {:%}'.format(v1.__repr__(),0.0,0.0)
    
                print '*'*65
                print 'Cross-product error components:'
                for i,v1 in enumerate(variables):
                    for j,v2 in enumerate(variables):
                        if i<j:
                            if vc_cp.has_key((v1,v2)):
                                print '({:}, {:}) = {:} or {:%}'.format(v1.__repr__(),v2.__repr__(),vc_lc[v1],vcont_cp[i,j])
                            else:
                                print '({:}, {:}) = {:} or {:%}'.format(v1.__repr__(),v2.__repr__(),0.0,0.0)
    
            return (vc_lc,vc_qc,vc_cp)
    
    def __str__(self):
        mn,vr,sk,kt = self.moments()
        s = 'UncertainFunction:\n'
        s += ' > Mean................... {: }\n'.format(mn)
        s += ' > Variance............... {: }\n'.format(vr)
        s += ' > Skewness Coefficient... {: }\n'.format(sk)
        s += ' > Kurtosis Coefficient... {: }'.format(kt)
        return s

    def __repr__(self):
        return 'UF({:}, {:}, {:}, {:})'.format(*self.moments())

    def _get_inputs_for_soerp(self):
        variables = self.d().keys()
        
        # standardize the input derivatives
        slc = np.array([self.d(v)*v.std() for v in variables])
        sqc = np.array([0.5*self.d2(v)*v.var() for v in variables])

        nvar = len(variables)
        scp = np.zeros((nvar,nvar))
        for i,v1 in enumerate(variables):
            for j,v2 in enumerate(variables):
                if hash(v1)!=hash(v2):
                    scp[i,j] = self.d2c(v1,v2)*v1.std()*v2.std()
                else:
                    scp[i,j] = 0.0

        var_moments = np.array([[1,0,1]+list(v._moments[2:]) for v in variables])  
        
        f0 = self.x # from evaluation at input means
        
        inputs = (slc,sqc,scp,var_moments,f0)
        
        return inputs
    
    def __add__(self,val):
        return _make_UF_compatible_object(ADF.__add__(self,val))

    def __radd__(self,val):
        return _make_UF_compatible_object(ADF.__radd__(self,val))
        
    def __mul__(self,val):
        return _make_UF_compatible_object(ADF.__mul__(self,val))

    def __rmul__(self,val):
        return _make_UF_compatible_object(ADF.__rmul__(self,val))
        
    def __sub__(self,val):
        return _make_UF_compatible_object(ADF.__sub__(self,val))

    def __rsub__(self,val):
        return _make_UF_compatible_object(ADF.__rsub__(self,val))
        
    def __div__(self,val):
        return _make_UF_compatible_object(ADF.__div__(self,val))

    def __rdiv__(self,val):
        return _make_UF_compatible_object(ADF.__rdiv__(self,val))
        
    def __truediv__(self,val):
        return _make_UF_compatible_object(ADF.__truediv__(self,val))

    def __rtruediv__(self,val):
        return _make_UF_compatible_object(ADF.__rtruediv__(self,val))
        
    def __pow__(self,val):
        return _make_UF_compatible_object(ADF.__pow__(self,val))

    def __rpow__(self,val):
        return _make_UF_compatible_object(ADF.__rpow__(self,val))
    
    def __neg__(self):
        return _make_UF_compatible_object(ADF.__neg__(self))
        
    def __pos__(self):
        return _make_UF_compatible_object(ADF.__pos__(self))
    
    def __abs__(self):
        return _make_UF_compatible_object(ADF.__abs__(self))
    
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

def _make_UF_compatible_object(tmp):
    if isinstance(tmp,ADF):
        return UncertainFunction(tmp.x, tmp.d(), tmp.d2(), tmp.d2c())
    else: # for scalars, etc.
        return tmp

################################################################################

class UncertainVariable(UncertainFunction, ADV):
    """
    UncertainVariable objects track the effects of uncertainty, characterized 
    in terms of the first four standard moments of statistical distributions 
    (mean, variance, skewness and kurtosis coefficients). Most texts 
    only deal with first-order models, but this class uses a full second 
    order model, which requires a knowledge of the first eight central moments 
    of a distribution.

    Parameters
    ----------
    moments : array-like, optional
        The first eight moments (standardized) of the uncertain variable's 
        underlying statistical distribution (the first two values should be the
        mean and variance)
    
    rv : scipy.stats.rv_continous, optional
        If supplied, the ``moments`` kwarg is ignored and the first eight 
        standardized moments are calculated internally
    
    tag : str, optional
        A string identifier when information about this variable is printed to
        the screen
        
    Notes
    -----
    
    For a full report on the methods behind this class, see:
        
        N. D. Cox, "Tolerance Analysis by Computer," Journal of Quality 
        Technology, Vol. 11, No. 2, 1979.
        
    Here are the first eight moments of some standard distributions:
        
        - Normal Distribution: [0, 1, 0, 3, 0, 15, 0, 105]
        - Uniform Distribution: [0, 1, 0, 1.8, 0, 3.857, 0, 9]
        - Exponential Distribution: [0, 1, 2, 9, 44, 265, 1854, 14833]
    
    A distribution's raw moment (moment about the origin) is defined as::

                oo           
                 /           
                |            
           k    |   k        
        E(x ) = |  x *f(x) dx
                |            
               /             
               -oo
    
    where E(...) is the expectation operator, k is the order of the moment, and
    f(x) is the probability density function (pdf) of x. 
    
    To convert these to central moments (moment about the mean), we can simply
    use the helper function::
    
        >>> moments = raw2central(raw_moments)
    
    or we can use the mathematical definition to calculate the kth moment as::
    
                     oo           
                      /           
                     |            
                k    |        k        
        E((x-mu) ) = |  (x-mu) *f(x) dx
                     |            
                    /             
                    -oo
    
    This then needs to be standardized by normalizing each of the moments 
    (starting with the third moment) using the standard deviation::
        
        >>> sd = moment[1]**0.5
        >>> moment[k] = [moment[k]/sd**(k + 1) for k in range(2, 9)]
        
    The ``scipy.stats`` module contains many distributions from which we can 
    easily generate these moments for any distribution. Currently, only
    ``rv_continuous`` distributions are supported. It is important to follow
    the initialization syntax for creating any kind of rv_continuous object:
        
        - *Location* and *Scale* values must use the kwargs ``loc`` and 
          ``scale``
        - *Shape* values are passed in as arguments before the location and 
          scale
        
    The mathematical operations that can be performed on Uncertain... objects
    will work for any moments or distribution supplied, but may not be misleading
    if the supplied moments or distribution is not accurately defined. Here are
    some guidelines for creating UncertainVariable objects using some of the
    most common statistical distributions:
        
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
    Using the first eight distribution moments::
        
        >>> x1 = uv([24, 1, 0, 3, 0, 15, 0, 105])            # normally distributed
        >>> x2 = uv([37, 16, 0, 3, 0, 15, 0, 105])           # normally distributed
        >>> x3 = uv([0.5, 0.25, 2, 9, 44, 265, 1854, 14833]) # exponentially distributed
        >>> Z = (x1*x2**2)/(15*(1.5 + x3))
        >>> Z
        UF(1176.45, 99699.6822919, 0.708013052954, 6.16324345122)

    The result shows the mean, variance, and standardized skewness and kurtosis
    of the output variable Z.
    
    Same example, but now using ``rv_continous`` objects::
        
        >>> import scipy.stats as ss
        >>> x1 = uv(rv=ss.norm(loc=24, scale=1))  # normally distributed
        >>> x2 = uv(rv=ss.norm(loc=37, scale=4))  # normally distributed
        >>> x3 = uv(rv=ss.expon(scale=0.5))  # exponentially distributed

    The results may be slightly different from using the moments manually since
    moment calculations can suffer from numerical errors during the integration
    of the expectation equations above, but they will be close to each other.
    
    Basic math operations may be applied to distributions, where all 
    statistical calculations are performed using method of moments. Built-in
    trig-, logarithm-, etc. functions should be used when possible since they
    support both scalar values and uncertain objects.
    
    At any time, the 8 standardized moments can be retrieved using::
        
        >>> x1.moments
        [24.0, 1.0, 0.0, 3.0000000000000053, 0.0, 15.000000000000004, 0.0, 105.0]
    
    Important
    ---------
    
    One final thing to note is that some answers suffer from the use of a 
    second-order approximation to the method of moment equations. For example, 
    the equation f(x) = x*sin(x) has this issue::
        
        >>> x = uv(rv=ss.norm(loc=0, scale=1)) # standard normal distribution
        >>> x*sin(x)
        UF(1.0, 2.0, 2.82842712475, 15.0)
    
    This is the precise answer for f(x) = x**2, which just so happens to be the
    second-order Taylor series approximation of x*sin(x). The correct answer 
    for [mean,variance,skewness,kurtosis] here can be calculated by::
        
        >>> mu = 0.0
        >>> sigma = 1.0
        >>> n = ss.norm(loc=mu, scale=sigma)
        >>> rm = [n.dist.expect(lambda x: (x*math.sin(x))**k, loc=mu, 
        ...       scale=sigma) for k in (1, 2, 3, 4)]
        >>> cm = raw2central(rm)
        >>> mean = rm[0]
        >>> var = cm[1]
        >>> std = var**0.5
        >>> skew = cm[2]/std**3
        >>> kurt = cm[3]/std**4
        >>> [mean, var, skew, kurt]
        [0.6065306597126335, 0.335123483683477, 0.6539519887886938, 2.558413439743406]
    
    Thus, care should be taken to make sure that the equations used are
    effectively quadratic within the respective input variable distribution
    ranges or you will see approximation errors like the example above.
    
    """
    
    def __init__(self,moments=[],rv=None,tag=None):
        assert not all([not moments, not rv]), 'Either the moments must be put in manually or a "rv_continuous" object from the "scipy.stats" module must be supplied'

        if rv is not None:
            loc = rv.kwds.get('loc', 0.0)
            scale = rv.kwds.get('scale', 1.0)
            shape = rv.args
            
            mn = rv.mean()
            sd = rv.std()

            # since the distribution parameters can only passed in as an arg
            # OR a kwd, check the kwd as well if there wasn't any luck with the
            # args above, otherwise, default to loc = 0 and scale = 1
            
            if shape:
                assert rv.dist.numargs>=1, 'The distribution provided doesn\'t support a "shape" parameter'
                expect = lambda k: rv.dist.expect(lambda x: x**k, args=shape, 
                                                  loc=loc, scale=scale)
                raw_moments = [expect(k) for k in range(1, 9)]
                moments = raw2central(list(raw_moments))
                for k in range(2, 8):
                    moments[k] = moments[k]/sd**(k + 1)
            
            else:
                assert rv.dist.numargs==0, 'The distribution provided requires a third "shape" parameter'
                expect = lambda k: rv.dist.expect(lambda x: x**k)
                raw_moments = [expect(k) for k in range(1, 9)]            
                moments = raw2central(list(raw_moments))
            
            # update the 1st and second moment values for SOERP calculations
            moments[0] = mn    # mean
            moments[1] = sd**2 # variance

            self._dist = rv
            
        else:
            self._dist = None
            
#        print 'moments:',moments
        ADV.__init__(self,moments[0],tag=tag)
        self._moments = moments
    
#    @property
    def mean(self):
        return self.moments(0)
    
#    @property
    def var(self):
        return self.moments(1)
		
#    @property
    def std(self):
        return self.var()**0.5
        
#    @property
    def skew(self):
        return self.moments(2)
    
#    @property
    def kurt(self):
        return self.moments(3)
    
#    @property
    def moments(self,idx=None):
        if idx is not None and idx<len(self._moments):
            return self._moments[idx]
        else:
            return self._moments
        
	def set_mean(self,mn):
		"""
		Modify the first moment via the mean
		"""
		self._moments[0] = mn
	
	def set_std(self,sd):
		"""
		Modify the second moment via the standard deviation
		"""
		self._moments[1] = sd**2
	
	def set_var(self,vr):
		"""
		Modify the second moment via the variance
		"""
		self._moments[1] = vr
	
	def set_skew(self,sk):
		"""
		Modify the third moment via the standardized skewness coefficient
		"""
		self._moments[2] = sk
	
	def set_kurt(self,kt):
		"""
		Modify the fourth moment via the standardized kurtosis coefficient
		"""
		self._moments[3] = kt
	
	def set_moments(self,m):
		"""
		Modify the first eight moments of the UncertainVariable's distribution
		"""
		assert len(m)==8, 'Input moments must include eight values'
		self._moments = m
		
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
        elif self._dist is not None:
            name = self._dist.dist.name
        else:
            name = 'UV'
        return name+'({:}, {:}, {:}, {:})'.format(
                self.mean(),self.var(),self.skew(),self.kurt())

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        pass
    else:
        def plot(self, vals=None, **kwargs):
            """Plot the distribution of the input variable.
            
            NOTE: This requires defining the input using a distribution from
            the ``scipy.stats`` module.
            
            """
            if self._dist is not None:
                if vals is None:
                    low = self._dist.ppf(0.0001)
                    high = self._dist.ppf(0.9999)
                else:
                    low = min(vals)
                    high = max(vals)
                vals = np.linspace(low,high,500)
                p = plt.plot(vals,self._dist.pdf(vals),**kwargs)
                plt.title(repr(self))
                plt.xlim(low-(high-low)*0.1,high+(high-low)*0.1)
                plt.show()
            else:
                raise NotImplemented("Cannot determine a distribution's pdf only by its moments (yet). Please use a scipy distribution if you want to plot.")
                
        
uv = UncertainVariable # a nicer form for the user

def raw2central(v):
    """Convert raw moments (1 to len(v)) to central moments"""
    def nci(n,i):
        return math.factorial(n)/(math.factorial(i)*math.factorial(n-i))
    
    v = [1]+v
    central_moments = []
    for k in range(len(v)):
        val = 0.0
        
        # use the recursion definition to transform
        for j in range(k+1):
            val += (-1)**j*nci(k,j)*v[k-j]*v[1]**j
        central_moments.append(val)
    
    return central_moments[1:]
