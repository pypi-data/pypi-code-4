# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 12:52:09 2013

@author: tisimst
"""
from random import randint
import math
#import copy

__version_info__ = (1, 0)
__version__ = '.'.join(map(str, __version_info__))

__author__ = 'Abraham D. Lee (ADL)'

__numeric_operators__ = [
    # these are the class methods that make any class emulate numeric objects
    'add','radd',
    'mul','rmul',
    'sub','rsub',
    'div','rdiv',
    'truediv','rtruediv',
    'pow','rpow',
    'neg','pos',
    'abs']
	
__all__ = ['AD','ADV','ADF']

CONSTANT_TYPES = (float,int,complex,long)

#def vectorize(func):
#    """
#    Converts a function that accepts one args (like 'sin') to one that
#    performs element-wise operations on the arg.
#    """
#    def wrapped_function(x):
#        if hasattr(x,'__getitem__'):
#            return [func(xi) for xi in x]
#        else:
#            return func(x)
#    
#    f = wrapped_function
#    # let's restore the useful information
#    f.__doc__ = func.__doc__
#    f.__name__ = func.__name__
#    
#    return f
#
def to_auto_diff(x):
    """
    Transforms x into a constant automatically differentiated function (ADF),
    unless it is already an ADF (in which case x is returned unchanged).

    Raises an exception unless 'x' belongs to some specific classes of
    objects that are known not to depend on AffineScalarFunc objects
    (which then cannot be considered as constants).
    """

    if isinstance(x, ADF):
        return x

    #! In Python 2.6+, numbers.Number could be used instead, here:
    if isinstance(x, CONSTANT_TYPES):
        # No variable => no derivative to define:
        return ADF(x, {}, {}, {})

#def partial_derivative(f, param_num):
#    """
#    Returns a function that numerically calculates the partial
#    derivative of function f with respect to its argument number
#    param_num.
#    """
#
#    def partial_derivative_of_f(*args):
#        """
#        Partial derivative, calculated with the (-epsilon, +epsilon)
#        method, which is more precise than the (0, +epsilon) method.
#        """
#        # f_nominal_value = f(*args)
#
#        shifted_args = list(args)  # Copy, and conversion to a mutable
#
#        # The step is relative to the parameter being varied, so that
#        # shifting it does not suffer from finite precision:
#        step = 1e-8*abs(shifted_args[param_num])
#        if not step:
#            # Arbitrary, but "small" with respect to 1, and of the
#            # order of the square root of the precision of double
#            # precision floats:
#            step = 1e-8
#
#        shifted_args[param_num] += step
#        shifted_f_plus = f(*shifted_args)
#        
#        shifted_args[param_num] -= 2*step  # Optimization: only 1 list copy
#        shifted_f_minus = f(*shifted_args)
#
#        return (shifted_f_plus - shifted_f_minus)/2/step
#
#    return partial_derivative_of_f
#
#def second_partial_derivative(f, param_num):
#    """
#    Returns a function that numerically calculates the second partial
#    derivative of function f with respect to its argument number.
#    """
#    def second_partial_derivative_of_f(*args):
#        """
#        Partial derivative, calculated with the (-epsilon, +epsilon)
#        method, which is more precise than the (0, +epsilon) method.
#        """
#        f_nominal_value = f(*args)
#
#        shifted_args = list(args)  # Copy, and conversion to a mutable
#
#        # The step is relative to the parameter being varied, so that
#        # shifting it does not suffer from finite precision:
#        step = 1e-8*abs(shifted_args[param_num])
#        if not step:
#            # Arbitrary, but "small" with respect to 1, and of the
#            # order of the square root of the precision of double
#            # precision floats:
#            step = 1e-8
#
#        shifted_args[param_num] += step
#        shifted_f_plus = f(*shifted_args)
#        
#        shifted_args[param_num] -= 2*step  # Optimization: only 1 list copy
#        shifted_f_minus = f(*shifted_args)
#
#        return (shifted_f_plus - 2*f_nominal_value + shifted_f_minus)/step**2
#
#    return second_partial_derivative_of_f
#
#def cross_partial_derivative(f, param_num1, param_num2):
#    """
#    Returns a function that numerically calculates the cross-second partial
#    derivative of function f with respect to its two argument numbers.
#    """
#    if param_num1==param_num2:
#        return second_partial_derivative(f,param_num1)
#        
#    def cross_partial_derivative_of_f(*args):
#        """
#        Partial derivative, calculated with the (-epsilon, +epsilon)
#        method, which is more precise than the (0, +epsilon) method.
#        """
##        f_nominal_value = f(*args)
#
#        shifted_args = list(args)  # Copy, and conversion to a mutable
#
#        # The step is relative to the parameter being varied, so that
#        # shifting it does not suffer from finite precision:
#        step1 = 1e-8*abs(shifted_args[param_num1])
#        step2 = 1e-8*abs(shifted_args[param_num2])
#        if not step1:
#            # Arbitrary, but "small" with respect to 1, and of the
#            # order of the square root of the precision of double
#            # precision floats:
#            step1 = 1e-8
#        if not step2:
#            # Arbitrary, but "small" with respect to 1, and of the
#            # order of the square root of the precision of double
#            # precision floats:
#            step2 = 1e-8
#
#        shifted_args[param_num1] += step1
#        shifted_args[param_num2] += step2
#        shifted_f_plus_plus = f(*shifted_args)
#        
#        shifted_args[param_num1] -= 2*step1  # Optimization: only 1 list copy
#        shifted_f_minus_plus = f(*shifted_args)
#
#        shifted_args[param_num1] += 2*step1
#        shifted_args[param_num2] -= 2*step2
#        shifted_f_plus_minus = f(*shifted_args)
#        
#        shifted_args[param_num1] -= 2*step1  # Optimization: only 1 list copy
#        shifted_f_minus_minus = f(*shifted_args)
#
#        return ((shifted_f_plus_plus - shifted_f_minus_plus)-\
#                (shifted_f_plus_minus - shifted_f_minus_minus))/4/step1/step2
#
#    return cross_partial_derivative_of_f
#
#class NumericalDerivatives(object):
#    """
#    Convenient access to the partial derivatives of a function,
#    calculated numerically.
#    """
#    # This is not a list because the number of arguments of the
#    # function is not known in advance, in general.
#
#    def __init__(self, function, order):
#        """
#        'function' is the function whose derivatives can be computed.
#        """
#        self._function = function
#        self._order = order
#
#    def __getitem__(self, n, order=1):
#        """
#        Returns the n-th numerical derivative of the function.
#        """
#        if order==1:
#            return partial_derivative(self._function, n)
#        elif order==2:
#            if hasattr(n,'__getitem__'):
#                return cross_partial_derivative(self._function,n[0],n[1])
#            else:
#                return second_partial_derivative(self._function,n)
#            
#
#def wrap(f,deriv_wrt_args=None,deriv2_wrt_args=None,deriv2c_wrt_args=None):
#    """
#    Wraps an arbitrary function f so that it can accept ADV/ADF objects and 
#    return an ADF object that contains first and second partial derivatives wrt
#    ADV objects.
#    
#    Parameters
#    ----------
#    f : function
#        Any function that returns a scalar (not a list or array-like object)
#    
#    Optional
#    --------
#    deriv_wrt_args : list
#        1st derivatives of f with respect to its input arguments (pure linear
#        terms)
#    deriv2_wrt_args : list
#        2nd derivatives of f with respect to its input arguments (pure 
#        quadratic terms)
#    deriv2c_wrt_args : list
#        2nd cross-product derivatives of f with respect to its input arguments
#        (i.e., if f(x,y), then this only contains d^2f/dxdy). This list should
#        contain the upper triangle of the hessian matrix (not including the
#        diagonal, pure quadratic terms), with entries arranged row by row.
#        
#        Thus, if the hessian of a function of three variables is:
#            
#                   | . d^2f/dx1dx2  d^2f/dx1dx3|
#            H(f) = | .      .       d^2f/dx2dx3|
#                   | .      .            .     |
#        
#        then deriv2c_wrt_args = [d^2f/dx1dx2, d^2f/dx1dx3, d^2f/dx2dx3]
#        
#    """
#    
#    if deriv_wrt_args is None:
#        deriv_wrt_args = NumericalDerivatives(f,1)
#    else:
#        # Derivatives that are not defined are calculated numerically,
#        # if there is a finite number of them (the function lambda
#        # *args: fsum(args) has a non-defined number of arguments, as
#        # it just performs a sum):
#        try:  # Is the number of derivatives fixed?
#            len(deriv_wrt_args)
#        except TypeError:
#            pass
#        else:
#            deriv_wrt_args = [
#                partial_derivative(f, k) if derivative is None
#                else derivative
#                for (k, derivative) in enumerate(deriv_wrt_args)]
#
#    if deriv2_wrt_args is None:
#        deriv2_wrt_args = NumericalDerivatives(f,2)
#    else:
#        # Derivatives that are not defined are calculated numerically,
#        # if there is a finite number of them (the function lambda
#        # *args: fsum(args) has a non-defined number of arguments, as
#        # it just performs a sum):
#        try:  # Is the number of derivatives fixed?
#            len(deriv2_wrt_args)
#        except TypeError:
#            pass
#        else:
#            deriv2_wrt_args = [
#                second_partial_derivative(f, k) if derivative is None
#                else derivative
#                for (k, derivative) in enumerate(deriv2_wrt_args)]
#    
#    if deriv2c_wrt_args is None:
#        deriv2c_wrt_args = NumericalDerivatives(f,2)
#    else:
#        try:
#            len(deriv2c_wrt_args)
#        except TypeError:
#            pass
#        else:
#            deriv2c_wrt_args = [[
#                cross_partial_derivative(f,k1,k2) if derivative is None and k1<k2
#                else derivative
#                for (k1, derivative) in enumerate(deriv2c_wrt_args)]
#                for (k2, derivative) in enumerate(deriv2c_wrt_args)]
#    
#    
#    
#    # THE USUAL CODE BELOW NEEDS TO BE MODIFIED ###############################
#    
##    ad_funcs = map(to_auto_diff,(self,val))
##
##    x = ad_funcs[0].x
##    y = ad_funcs[1].x
##    
##    ########################################
##    # Nominal value of the constructed ADF:
##    f_nominal   = x + y
##    
##    ########################################
##    variables = self._get_variables(ad_funcs)
##    
##    if not variables or isinstance(f_nominal, bool):
##        return f
##
##    ########################################
##
##    # Calculation of the derivatives with respect to the arguments
##    # of f (ad_funcs):
##
##    lc_wrt_args = [1., 1.]
##    qc_wrt_args = [0., 0.]
##    cp_wrt_args = 0.
##
##    ########################################
##    # Calculation of the derivative of f with respect to all the
##    # variables (Variable) involved.
##
##    lc_wrt_vars,qc_wrt_vars,cp_wrt_vars = _calculate_derivatives(
##                                ad_funcs,variables,lc_wrt_args,qc_wrt_args,
##                                cp_wrt_args)
##                                
##    # The function now returns an ADF object:
##    return ADF(f_nominal, lc_wrt_vars, qc_wrt_vars, cp_wrt_vars)

def _calculate_derivatives(ad_funcs,variables,lc_wrt_args,qc_wrt_args,
                           cp_wrt_args):
    # Initial value (is updated below):
    lc_wrt_vars = dict((var, 0.) for var in variables)
    qc_wrt_vars = dict((var, 0.) for var in variables)
    cp_wrt_vars = {}
    for i,var1 in enumerate(variables):
        for j,var2 in enumerate(variables):
            if i<j:
                cp_wrt_vars[(var1,var2)] = 0.

    # The chain rule is used (we already have
    # derivatives_wrt_args):
    
#        print '***************************************************************'
#        print 'variables: {:}'.format(variables)
#        print 'ad_funcs : {:}'.format(ad_funcs)
#        print 'lc_wrt_args: {:}'.format(lc_wrt_args)
#        print 'qc_wrt_args: {:}'.format(qc_wrt_args)
#        print 'cp_wrt_args: {:}'.format(cp_wrt_args)
    for j,var1 in enumerate(variables):
        for k,var2 in enumerate(variables):
            for (f, dh, d2h) in zip(ad_funcs,lc_wrt_args,qc_wrt_args):
                
                if j==k:
#                        print '(j,{:})==(k,{:})'.format(j,k)
                    tmp = dh*f.d(var1)
#                        print 'adding {:} to first derivative of var: {:}'.format(tmp,var1)
                    lc_wrt_vars[var1] += tmp
#                        print 'lc_wrt_vars[{:}] = {:}'.format(var1,lc_wrt_vars[var1])

                    tmp = dh*f.d2(var1) + d2h*f.d(var1)**2
#                        print 'adding {:} to second derivative of var: {:}'.format(tmp,var1)
                    qc_wrt_vars[var1] += tmp
#                        print 'qc_wrt_vars[{:}] = {:}'.format(var1,qc_wrt_vars[var1])

                elif j<k:
#                        print '(j,{:})<(k,{:})'.format(j,k)
                    tmp = dh*f.d2c(var1,var2)
#                        print 'adding {:} to second cross-derivative of var: {:} and var: {:}'.format(tmp,var1,var2)
                    cp_wrt_vars[(var1,var2)] += tmp
#                        print 'cp_wrt_vars[({:},{:})] = {:}'.format(var1,var2,qc_wrt_vars[var1])
                    tmp = d2h*f.d(var1)*f.d(var2)
#                        print 'adding {:} to second cross-derivative of var: {:} and var: {:}'.format(tmp,var1,var2)
                    cp_wrt_vars[(var1,var2)] += tmp
#                        print 'cp_wrt_vars[({:},{:})] = {:}'.format(var1,var2,qc_wrt_vars[var1])

#                print 'done iterating over args'
            if j==k and len(ad_funcs)>1:
#                    print '(j,{:})==(k,{:})'.format(j,k)
                tmp = 2*cp_wrt_args*ad_funcs[0].d(var1)*ad_funcs[1].d(var1)
#                    print 'adding to {:} to second derivative of var: {:}'.format(tmp,var1)
                qc_wrt_vars[var1] += tmp
#                    print 'qc_wrt_vars[{:}] = {:}'.format(var1,qc_wrt_vars[var1])

            elif j<k and len(ad_funcs)>1:
#                    print '(j,{:})<(k,{:})'.format(j,k)
                tmp = cp_wrt_args*(ad_funcs[0].d(var1)*ad_funcs[1].d(var2)+ad_funcs[0].d(var2)*ad_funcs[1].d(var1))
#                    print 'adding {:} to second cross-derivative of var: {:} and var: {:}'.format(tmp,var1,var2)
                cp_wrt_vars[(var1,var2)] += tmp
#                    print 'cp_wrt_vars[({:},{:})] = {:}'.format(var1,var2,qc_wrt_vars[var1])
                
#            print '********************* done with var: {:} *********************'.format(var1)
        
    return (lc_wrt_vars,qc_wrt_vars,cp_wrt_vars)
    
class ADF(object):
    """
    The ADF (Automatically Differentiated Function) class is an extension of 
    the ADV class, in that any ADF object is a result of a previous operation 
    on either two ADV objects, one ADV object and one ADF object, or two ADF 
    objects. An ADF object will have additional class members 'lc', 'qc', and 
    'cp' to contain first order derivatives, second-order derivatives, and 
    cross-product derivatives, respectively, of all ADV objects in the ADF's 
    lineage. When requesting a cross-product term, 'cp', a tuple of the two ADV
    objects is used as input. Either order of objects may be used since, 
    mathematically, they are equivalent. For example, if z(x,y), then::

          2       2
         d z     d z
        ----- = -----
        dx dy   dy dx
    
    
    Example
    -------
    Initialize some ADV objects (tag not required, but useful)::

        >>> x = AD(1,'x')
        >>> y = AD(2,'y')
        
    Now some basic math, showing the derivatives of the final result. Note that
    if we don't supply an input to the derivative methods, a dictionary with
    all derivatives wrt the subsequently used ADV objects is returned::
        
        >>> z = x+y
        >>> z.d()
        {x(1.0): 1.0, y(2.0): 1.0}
        >>> z.d2()
        {x(1.0): 0.0, y(2.0): 0.0}
        >>> z.d2c()
        {(x(1.0), y(2.0)): 0.0}
        
    Let's take it a step further now and see if relationships hold::
        
        >>> w = x*z # same as x*(x+y) = x**2 + x*y
        >>> w.d(x)  # dw/dx = 2*x+y = 2*(1)+2 = 4
        4.0
        >>> w.d2(x) # d2w/dx2 = 2
        2.0
        >>> w.d2(y) # d2w/dy2 = 0
        0.0
        >>> w.d2c(x,y) # d2w/dxdy = 1
        1.0

    For convenience, we can get the gradient and hessian if we supply the order
    of the variables (useful in optimization routines)::
        
        >>> w.gradient([x,y])
        [4.0, 1.0]
        >>> w.hessian([x,y])
        [[2.0, 1.0], [1.0, 0.0]]
        
    You'll note that these are constructed using lists and nested lists instead
    of depending on numpy arrays, though if numpy is installed, they can look
    much nicer and are a little easier to work with::
        
        >>> import numpy as np
        >>> np.array(w.hessian([x,y]))
        array([[ 2.,  1.],
               [ 1.,  0.]])

    """
    def __init__(self,value,lc,qc,cp):
        self.x = float(value)
        self._lc = lc
        self._qc = qc
        self._cp = cp
    
    def __hash__(self):
        return id(self)
        
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return 'ADF('+str(self.x)+')'

    def d(self,x=None):
        """
        Returns first-derivative with respect to x=ADV object. If x=None, then
        all first derivatives are returned. If no derivatives are found based 
        on x, zero is returned.
        """
        if x is not None:
            if isinstance(x,ADF):
                try:
                    tmp = self._lc[x]
                except KeyError:
                    tmp = 0.0
                return tmp
            else:
                return 0.0
        else:
            return self._lc
    
    def d2(self,x=None):
        """
        Returns second-derivative with respect to x=ADV object. If x=None, then
        all second derivatives are returned. If no derivatives are found based 
        on x, zero is returned.
        """
        if x is not None:
            if isinstance(x,ADF):
                try:
                    tmp = self._qc[x]
                except KeyError:
                    tmp = 0.0
                return tmp
            else:
                return 0.0
        else:
            return self._qc
    
    def d2c(self,x=None,y=None):
        """
        Returns second cross-derivative with respect to x=ADV object and y=ADV 
        object. If x=None and y=None then all second derivatives are returned.
        If x==y, then the second derivative of x is returned. If no derivatives
        are found based on x and y, zero is returned.
        """
        if (x is not None) and (y is not None):
            if hash(x)==hash(y):
                tmp = self.d2(x)
            else:
                if isinstance(x,ADF) and isinstance(y,ADF):
                    try:
                        tmp = self._cp[(x,y)]
                    except KeyError:
                        try:
                            tmp = self._cp[(y,x)]
                        except KeyError:
                            tmp = 0.0
                else:
                    return 0.0
                
            return tmp
        elif ((x is not None) and not (y is not None)) or ((y is not None) and not (x is not None)):
            return 0.0
        else:
            return self._cp
    
    def gradient(self,variables):
        if not hasattr(variables,'__getitem__'):
            return [self.d(variables)]
        
        assert all([isinstance(v,ADF) for v in variables]), 'Can only show gradient with respect to ADV objects'
        
        grad = [self.d(v) for v in variables]
        return grad
        
    def hessian(self,variables):
        if not hasattr(variables,'__getitem__'):
            return [[self.d2(variables)]]
            
        assert all([isinstance(v,ADF) for v in variables]), 'Can only show hessian with respect to ADV objects'
        
        hess = []
        for v1 in variables:
            hess.append([self.d2c(v1,v2) for v2 in variables])
        return hess
        
    def _get_variables(self,ad_funcs):
        # List of involved variables (Variable objects):
        variables = set()
        for expr in ad_funcs:
            variables |= set(expr.d())
        return variables
    
    def __add__(self, val):
        
        ad_funcs = map(to_auto_diff,(self,val))

        x = ad_funcs[0].x
        y = ad_funcs[1].x
        
        ########################################
        # Nominal value of the constructed ADF:
        f   = x + y
        
        ########################################
        variables = self._get_variables(ad_funcs)
        
        if not variables or isinstance(f, bool):
            return f

        ########################################

        # Calculation of the derivatives with respect to the arguments
        # of f (ad_funcs):

        lc_wrt_args = [1., 1.]
        qc_wrt_args = [0., 0.]
        cp_wrt_args = 0.

        ########################################
        # Calculation of the derivative of f with respect to all the
        # variables (Variable) involved.

        lc_wrt_vars,qc_wrt_vars,cp_wrt_vars = _calculate_derivatives(
                                    ad_funcs,variables,lc_wrt_args,qc_wrt_args,
                                    cp_wrt_args)
                                    
        # The function now returns an ADF object:
        return ADF(f, lc_wrt_vars, qc_wrt_vars, cp_wrt_vars)
    
    def __radd__(self, val):
        """
        This method shouldn't need any modification if __add__ and __mul__ have
        been defined
        """
        return self+val

    def __mul__(self, val):
        ad_funcs = map(to_auto_diff,(self,val))

        x = ad_funcs[0].x
        y = ad_funcs[1].x
        
        ########################################
        # Nominal value of the constructed ADF:
        f   = x*y
        
        ########################################

        variables = self._get_variables(ad_funcs)
        
        if not variables or isinstance(f, bool):
            return f

        ########################################

        # Calculation of the derivatives with respect to the arguments
        # of f (ad_funcs):

        lc_wrt_args = [y, x]
        qc_wrt_args = [0., 0.]
        cp_wrt_args = 1.

        ########################################
        # Calculation of the derivative of f with respect to all the
        # variables (Variable) involved.

        lc_wrt_vars,qc_wrt_vars,cp_wrt_vars = _calculate_derivatives(
                                    ad_funcs,variables,lc_wrt_args,qc_wrt_args,
                                    cp_wrt_args)
                                    
        # The function now returns an ADF object:
        return ADF(f, lc_wrt_vars, qc_wrt_vars, cp_wrt_vars)
    
    def __rmul__(self, val):
        """
        This method shouldn't need any modification if __add__ and __mul__ have
        been defined
        """
        return self*val    
    
    def __div__(self, val):
        return self.__truediv__(val)
    
    def __truediv__(self,val):
        ad_funcs = map(to_auto_diff,(self,val))

        x = ad_funcs[0].x
        y = ad_funcs[1].x
        
        ########################################
        # Nominal value of the constructed ADF:
        f   = x/y
        
        ########################################

        variables = self._get_variables(ad_funcs)
        
        if not variables or isinstance(f, bool):
            return f

        ########################################

        # Calculation of the derivatives with respect to the arguments
        # of f (ad_funcs):

        lc_wrt_args = [1./y, -x/y**2]
        qc_wrt_args = [0., 2*x/y**3]
        cp_wrt_args = -1./y**2

        ########################################
        # Calculation of the derivative of f with respect to all the
        # variables (Variable) involved.

        lc_wrt_vars,qc_wrt_vars,cp_wrt_vars = _calculate_derivatives(
                                    ad_funcs,variables,lc_wrt_args,qc_wrt_args,
                                    cp_wrt_args)
                                    
        # The function now returns an ADF object:
        return ADF(f, lc_wrt_vars, qc_wrt_vars, cp_wrt_vars)
    
    
    def __rdiv__(self, val):
        """
        This method shouldn't need any modification if __add__ and __mul__ have
        been defined
        """
        return val*self**(-1)
    
    def __rtruediv__(self, val):
        """
        This method shouldn't need any modification if __add__ and __mul__ have
        been defined
        """
        return val*self**(-1)
    
    def __sub__(self, val):
        """
        This method shouldn't need any modification if __add__ and __mul__ have
        been defined
        """
        return self+(-1*val)

    def __rsub__(self,val):
        """
        This method shouldn't need any modification if __add__ and __mul__ have
        been defined
        """
        return -1*self+val

    def __pow__(self, val):
        ad_funcs = map(to_auto_diff,(self,val))
        
        x = ad_funcs[0].x
        y = ad_funcs[1].x
        
        ########################################
        # Nominal value of the constructed ADF:
        f   = x**y
        
        ########################################

        variables = self._get_variables(ad_funcs)
        
        if not variables or isinstance(f, bool):
            return f

        ########################################

        # Calculation of the derivatives with respect to the arguments
        # of f (ad_funcs):

        if x>0 and ad_funcs[1].d(ad_funcs[1])!=0:
            lc_wrt_args = [y*x**(y-1), x**y*math.log(x)]
            qc_wrt_args = [y*(y-1)*x**(y-2), (math.log(x))**2]
            cp_wrt_args = x**(y-1)*(x*math.log(x)+y)
        else:
            lc_wrt_args = [y*x**(y-1), 0.]
            qc_wrt_args = [y*(y-1)*x**(y-2), 0.]
            cp_wrt_args = 0.
            

        ########################################
        # Calculation of the derivative of f with respect to all the
        # variables (Variable) involved.

        lc_wrt_vars,qc_wrt_vars,cp_wrt_vars = _calculate_derivatives(
                                    ad_funcs,variables,lc_wrt_args,qc_wrt_args,
                                    cp_wrt_args)
                                    
        # The function now returns an ADF object:
        return ADF(f, lc_wrt_vars, qc_wrt_vars, cp_wrt_vars)

    def __rpow__(self,val):
        return to_auto_diff(val)**self
        
    def __neg__(self):
        return -1*self
    
    def __pos__(self):
        return self

    def __abs__(self):
        ad_funcs = map(to_auto_diff,[self])

        x = ad_funcs[0].x
        
        ########################################
        # Nominal value of the constructed ADF:
        f   = abs(x)
        
        ########################################

        variables = self._get_variables(ad_funcs)
        
        if not variables or isinstance(f, bool):
            return f

        ########################################

        # Calculation of the derivatives with respect to the arguments
        # of f (ad_funcs):

        # catch the x=0 exception
        try:
            lc_wrt_args = [x/abs(x)]
            qc_wrt_args = [1/abs(x)-(x**2)/abs(x)**3]
        except ZeroDivisionError:
            lc_wrt_args = [0.0]
            qc_wrt_args = [0.0]
            
        cp_wrt_args = 0.0

        ########################################
        # Calculation of the derivative of f with respect to all the
        # variables (Variable) involved.

        lc_wrt_vars,qc_wrt_vars,cp_wrt_vars = _calculate_derivatives(
                                    ad_funcs,variables,lc_wrt_args,qc_wrt_args,
                                    cp_wrt_args)
                                    
        # The function now returns an ADF object:
        return ADF(f, lc_wrt_vars, qc_wrt_vars, cp_wrt_vars)
        
    def __int__(self):
        return int(self.x)
    
    def __float__(self):
        return float(self.x)
    
    def __long__(self):
        return long(self.x)
    
    def __eq__(self,val):
        return float.__eq__(float(self),float(val))
    
    def __ne__(self,val):
        return not self==val

    def __lt__(self,val):
        return float.__lt__(float(self),float(val))
    
    def __le__(self,val):
        return (self < val) or (self==val)
    
    def __gt__(self,val):
        return float.__gt__(float(self),float(val))
    
    def __ge__(self,val):
        return (self>val) or (self==val)
    
    def __nonzero__(self):
        return float.__nonzero__(float(self))
        
class ADV(ADF):
    """
    A convenience class for distinguishing between FUNCTIONS (ADF) and VARIABLES
    """
    def __init__(self, value, tag=None):
        self.tag = tag
        self._hash = long(randint(1,100000000))
        super(ADV, self).__init__(value,{self:1.0},{self:0.0},{})
        
        # by generating this random hash, it should preserve relations even
        # after pickling and un-pickling
        
    def __repr__(self):
        if self.tag:
#            return self.tag + str((self.x,self.dx,self.dx2))
            return self.tag + '(' + str(self.x) + ')'
        else:
            return str(self)
    
    def __str__(self):
        return 'ADV(' + str(self.x) + ')'
            
    def __hash__(self):
#        if not self._hash:
#            self._hash = long(id(self))
#        print 'ADV hash =',self._hash
        return self._hash
#        return id(self)

def AD(x,tag=None):
    """
    Utility function for creating AUTOMATIC DIFFERENTIATION VARIABLES
    
    Parameters
    ----------
    x : scalar or array-like
        The nominal value of the variable. If an array is input, AD will return
        an array of ADV objects in the same type of array container (i.e., an
        input list will return a list, a numpy.ndarray will return an 
        numpy.ndarray, etc.).
    
    Optional
    --------
    tag : str
        A string identifier
        
    Returns
    -------
    a : an ADV object
        This object will contain information about its nominal value as any
        variable normally would with additional information about its first and
        second derivatives at the nominal value. It is always represented as a 
        tuple of these three values --> (nom,dx,dx2)
        
    Examples
    --------
    
    Creating an ADV object:
        
        >>> x = AD(2)
        >>> x
        ADV(2)
    
    Let's do some math:
        
        >>> y = AD(0.5)
        >>> x*y
        ADF(1.0)
        >>> x/y
        ADF(4.0)
        >>> z = x**y
        >>> z
        ADF(1.41421356237)
        >>> z.d(x)
        0.3535533905932738
        >>> z.d2(x)
        -0.08838834764831845
        >>> z.d2c(x,y)
        1.333811534061821
        
    We can also use the exponential, logarithm, and trigonometric functions:
        
        >>> from ad.admath import * # sin(), etc.
        >>> z = x*sin(y/3)
        >>> z
        ADF(0.331792265387)
        >>> z.d(x)
        0.16589613269341502
        >>> z.d(y)
        0.65742882104195
        >>> z.d2()
        {ADV(2.0): 0.0, ADV(0.5): -0.11059742179561001}
        >>> z.d2c(x,y)
        0.328714410520975

    If we use the ``tag`` key-word argument when creating ADV objects, the
    relationships between original variables and current functions becomes a
    little clearer:
        
        >>> x = AD(2, 'x')
        >>> y = AD(0.5, 'y')
        >>> z = x*sin(y/3)
        >>> z.d()
        {x(2.0): 0.16589613269341502, y(0.5): 0.65742882104195}
        >>> z.d2()
        {x(2.0): 0.0, y(0.5): -0.11059742179561001}
        >>> z.d2c()
        {(x(2.0), y(0.5)): 0.328714410520975}
        
    We can also initialize multiple ADV objects in the same constructor by
    supplying a sequence of values, but the ``tag`` keyword is not yet
    supported for multiple objects:
        
        >>> x,y,z = AD([2,0.5,3.1415])
        
    """
#    print 'Creating an ADV object out of a {:} type object with value: {:}'.format(type(x),x)
    if isinstance(x,ADF):
        return x
    elif hasattr(x,'__getitem__'):
        return [AD(xi) for xi in x]
    elif isinstance(x, CONSTANT_TYPES):
        return ADV(x,tag)
    else:
        raise NotImplemented('Automatic differentiation not yet supported for {:} objects'.format(type(x)))
