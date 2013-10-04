#:coding=utf8:

from decimal import (
    Decimal,
    Context,
    getcontext,
    setcontext,
    InvalidOperation,
    Inexact,
)

#def force_decimal(obj,  
__all__ = (
    'force_decimal',
    'pi',
    'exp',
    'cos',
    'sin',
    'log',
    'ln',
)

def force_decimal(d, precision_loss=True, numbers_only=False):
    """
    Coerces a value to a Decimal object. 

    If precision_loss is True then float objects are first converted
    to strings before being converted to Decimal objects. This can cause
    a loss of precision as the float objects are rounded. The 'str'
    method is used since it provides better precision than "%f" % float.

    If you wish to preserve as much information as possible you can call
    the method with precision_loss=False and method will be used that
    can convert the float without loosing information. This can, however,
    add extra information due to issues with binary floating point.
    
    See: Is there a way to convert a regular float to a Decimal?
    http://docs.python.org/library/decimal.html#decimal-faq

    If numbers_only is True, don't convert (some) non-number-like objects.
    Strings that can be converted to Decimals are still converted.
    """
    try:
        if isinstance(d, Decimal):
            return d
        elif isinstance(d, (int, long)):
            return Decimal(d)
        elif isinstance(d, float):
            return Decimal(str(d)) if precision_loss else float_to_decimal(d)
        elif isinstance(d, (basestring, unicode)):
            return Decimal(d)
    except InvalidOperation:
        pass

    if numbers_only:
        return d
    else:
        raise ValueError("Cannot convert object to Decimal: %r" % d)  

def float_to_decimal(f):
    """
    Convert a floating point number to a Decimal with no loss of information
    """
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return +result

def pi():
    """
    Compute Pi to the current precision.
    Taken from: http://docs.python.org/library/decimal.html#decimal-recipes

    >>> print pi()
    3.141592653589793238462643383
    """
    getcontext().prec += 2  # extra digits for intermediate steps
    three = Decimal(3)      # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    getcontext().prec -= 2
    return +s               # unary plus applies the new precision

def exp(x):
    """
    Return e raised to the power of x.  Result type matches input type.
    Taken from: http://docs.python.org/library/decimal.html#decimal-recipes

    >>> print exp(Decimal(1))
    2.718281828459045235360287471
    >>> print exp(Decimal(2))
    7.389056098930650227230427461
    >>> print exp(2.0)
    7.38905609893
    >>> print exp(2+0j)
    (7.38905609893+0j)

    """
    getcontext().prec += 2
    i, lasts, s, fact, num = 0, 0, 1, 1, 1
    while s != lasts:
        lasts = s
        i += 1
        fact *= i
        num *= x
        s += num / fact
    getcontext().prec -= 2
    return +s

def cos(x):
    """
    Return the cosine of x as measured in radians.
    Taken from: http://docs.python.org/library/decimal.html#decimal-recipes

    >>> print cos(Decimal('0.5'))
    0.8775825618903727161162815826
    >>> print cos(0.5)
    0.87758256189
    >>> print cos(0.5+0j)
    (0.87758256189+0j)
    """
    getcontext().prec += 2
    i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1
    while s != lasts:
        lasts = s
        i += 2
        fact *= i * (i-1)
        num *= x * x
        sign *= -1
        s += num / fact * sign
    getcontext().prec -= 2
    return +s

def sin(x):
    """
    Return the sine of x as measured in radians.
    Taken from: http://docs.python.org/library/decimal.html#decimal-recipes

    >>> print sin(Decimal('0.5'))
    0.4794255386042030002732879352
    >>> print sin(0.5)
    0.479425538604
    >>> print sin(0.5+0j)
    (0.479425538604+0j)
    """
    getcontext().prec += 2
    i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1
    while s != lasts:
        lasts = s
        i += 2
        fact *= i * (i-1)
        num *= x * x
        sign *= -1
        s += num / fact * sign
    getcontext().prec -= 2
    return +s

def log(self, base=10, context=None):
    """
    Returns a log of arbitrary precision using the method
    described here: http://www.programmish.com/?p=25

    Input must be a decimal

    >>> print log(Decimal("1.204"))
    0.0806264869218057475447822012
    >>> print log(Decimal("1.204"), 2)
    0.2678353920976150027151526692

    >>> import math
    >>> abs(math.log(1.204, 10) - float(log(Decimal("1.204")))) < 1e-15
    True
    >>> abs(math.log(1.827528759292, 10) - float(log(Decimal("1.827528759292")))) < 1e-15
    True
    """
    old_context = None
    if context is not None:
        old_context = getcontext()
        setcontext(context)

    cur_prec = getcontext().prec
    getcontext().prec += 2
    try:
        retValue = self
        baseDec = force_decimal(base)

        integer_part = Decimal(0)
        while retValue < 1:
            integer_part = integer_part - 1
            retValue = retValue * baseDec
        while retValue >= baseDec:
            integer_part = integer_part + 1
            retValue = retValue / baseDec

        retValue = retValue ** 10
        decimal_frac = Decimal(0)
        partial_part = Decimal(1)
        while cur_prec > 0:
            partial_part = partial_part / Decimal(10)
            digit = Decimal(0)
            while retValue >= baseDec:
                digit += 1
                retValue = retValue / baseDec
            decimal_frac = decimal_frac + digit * partial_part
            retValue = retValue ** 10
            cur_prec -= 1
    finally:
        # restore contexts
        getcontext().prec -= 2
        if old_context is not None:
            setcontext(old_context)

    return integer_part + decimal_frac

def ln(self, context=None):
    """
    Returns the natural log of the given Decimal

    Input must be a decimal

    >>> print ln(Decimal("1.204"))
    0.1856493468866292953586851357

    >>> import math
    >>> abs(math.log(1.204) - float(ln(Decimal("1.204")))) < 1e-15
    True
    >>> abs(math.log(1.827528759292) - float(ln(Decimal("1.827528759292")))) < 1e-15
    True
    """
    if hasattr(self, "ln"):
        return self.ln(context)
    else:
        return log(self, base=exp(Decimal("1.0"))) 
