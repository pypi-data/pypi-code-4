#!/usr/bin/env python"
"""`rational` an Implementation of Rational Numbers

The module provides rational arithmetic.
Additionally the module servers as example for the generic function package.

Usually you only need its :class:`Rational` class:

>>> from rational import Rational as R

Rational numbers can be constructed from integers:

>>> r2 = R(1, 2)
>>> r1 = R(1)
>>> r0 = R()

Construction from arbitrary objects is not possible:
>>> R("Urmel")  # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
...
NotImplementedError: Generic 'gf.go.__init__' has no implementation for type(s): rational.Rational, __builtin__.str


Rationals also have a decent string representation:

>>> r0
Rational()
>>> print r0
0
>>> r1
Rational(1)
>>> print r1
1
>>> r2
Rational(1, 2)
>>> print r2
1 / 2


Ordinary arithmetic works as expected:

>>> print R(1, 2) + R(1, 4)
3 / 4
>>> 1 + R(1, 2)
Rational(3, 2)
>>> print R(2) / 1000
1 / 500
>>> print R(-5,-10)
1 / 2
>>> print R(5, -10)
-1 / 2
>>> print -R(5, -10)
1 / 2

Conversion from longs also works:

>>> R(1L)
Rational(1L)

Mixed constituents are converted to long:

>>> R(1, 2L)
Rational(1L, 2L)

Comparison also works as expected:

>>> R(1, 2) == R(2, 4)
True
>>> R(4, 2) == 2
True
>>> 1 == R(1, 2)
False
>>> 3L == R(10, 5)
False
>>> R(1, 2) < R(3, 4)
True
>>> R(1, 2) < 1
True
>>> R(1, 2) < 1L
True
>>> R(1, 2) > R(1, 4)
True
>>> 1 > R(1, 2)
True
>>> 2L > R(10, 7)
True
>>> R(10, 2) >= R(5)
True
>>> R() != R(1)
True
>>> R() != 0
False
>>> 1 != R(1)
False

The :mod:`decimal` module is supported as well:

>>> from decimal import Decimal as D
>>> R(D("0.375"))
Rational(3, 8)
>>> R(1, 2) + D("1.5")
Rational(2)

Even very long decimals do work:

>>> R(D("7.9864829273648218372937") * 4)
Rational(79864829273648218372937L, 2500000000000000000000L)

Comparisons with :class:`decimal.Decimal` instances are also supported:

>>> D("1.2") == R(24, 20)
True
>>> D("1.2") >= R(23, 20)
True
>>> R(23, 20) <= D("1.2")
True

Rationals can also converted to floats:

>>> float(R(1, 4))
0.25
"""


from decimal import Decimal
# Make `gf` importable from the examples directory
_python_path_tweaked = False
while 1:
    try:
        from gf import (method, Object,
                __init__, __float__,
                __add__, __sub__, __mul__, __div__, __neg__,
                __eq__, __ne__, __lt__, __gt__, __le__, __ge__,
                __out__, __spy__, Writer)
    except ImportError:
        if _python_path_tweaked:
            raise
        else:
            import sys, os
            sys.path.insert(0,
                    os.path.abspath(
                        os.path.normpath(
                            os.path.join(
                                os.path.dirname(__file__), os.pardir))))
            _python_path_tweaked = True
            del sys, os
    else:
        break



def gcd(a, b):
    """:func:`gcd` computes GCD of to numbers."""
    while b != 0:
        a, b = b, a % b
    return a


class Rational(Object):
    """:class:`Rational` is our rational numbers class."""


@method(Rational, int, int, bool)
def __init__(rational, numerator, denominator, cancel):
    """Initialize the object with `numerator` and `denominator`.
    
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.
    :param denominator: The denominator.
    :param cancel: A flag indicating, that `numerator`and `denominator`
                   should be canceled.
    """
    if denominator == 0:
        raise ZeroDivisionError("Denominator can not be zero")
    if cancel:
        g = gcd( numerator, denominator )
        n = numerator / g
        d = denominator / g
    else:
        n = numerator
        d = denominator
    rational.numerator = n
    rational.denominator = d

@method(Rational, long, long, bool)
def __init__(rational, numerator, denominator, cancel):
# We just pretend we are dealing with longs
    """Initialize the object with `numerator` and `denominator`.
    
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.
    :param denominator: The denominator.
    :param cancel: A flag indicating, that `numerator`and `denominator`
                   should be canceled.

    Use :meth:`gf.__init__.super` to call the multi-method that has the
    (:class:`Rational`, `int`, `int`, `bool`) signature.
    """
    __init__.super(Rational, int, int, bool)(
            rational, numerator, denominator, cancel)

CANCEL_EAGERLY = True

@method(Rational, int, int)
def __init__(rational, numerator, denominator):
    """Initialize the object with `numerator` and `denominator`.
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.
    :param denominator: The denominator.

    Call :func:`__init__` with all passed arguments and
    with the value of `CANCEL_EAGERLY` for the `cancel`-flag.
    """
    __init__(rational, numerator, denominator, CANCEL_EAGERLY)

@method(Rational, long, long)
def __init__(rational, numerator, denominator):
    """Initialize the object with `numerator` and `denominator`.
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.
    :param denominator: The denominator.

    Call :func:`__init__` with all passed arguments and
    with the value of `CANCEL_EAGERLY` for the `cancel`-flag.
    """
    __init__(rational, numerator, denominator, CANCEL_EAGERLY)

@method(Rational, int, long)
def __init__(rational, numerator, denominator):
    """Initialize the object with `numerator` and `denominator`.
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.
    :param denominator: The denominator.

    Convert the `numerator` to `long` and call 
    :func:`__init__` with all arguments."""
    __init__(rational, long(numerator), denominator)

@method(Rational, long, int)
def __init__(rational, numerator, denominator):
    """Initialize the object with `numerator` and `denominator`.
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.
    :param denominator: The denominator.

    Convert the `denominator` to `long` and call 
    :func:`__init__` with all arguments."""
    __init__(rational, numerator, long(denominator))

@method(Rational, int)
def __init__(rational, numerator):
    """Initialize the object with `numerator`.
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.

    Call :func:`__init__` with the `denominator` set to 1."""
    __init__(rational, numerator, 1)

@method(Rational, long)
def __init__(rational, numerator):
    """Initialize the object with `numerator`.
    :param rational: The rational number to be initialized.
    :param numerator: The numerator.

    Call :func:`__init__` with the `denominator` set to 1L."""
    __init__(rational, numerator, 1L)

@method(Rational)
def __init__(rational):
    """Initialize the object to be 0.
    :param rational: The rational number to be initialized.

    Call :func:`__init__` with the `numerator` set to 0."""
    __init__(rational, 0)

@method(Rational, Rational)
def __init__(rational0, rational1):
    """Initialize the object from another rational.
    :param rational0: The rational number to be initialized.
    :param rational1: The rational number the attributes are copied from.
    """
    rational0.numerator = rational1.numerator
    rational0.denominator = rational1.denominator

@method(Rational, Rational, Rational)
def __init__(rational0, rational1, rational2):
    """Initialize the object from another rational.
    :param rational0: The rational number to be initialized.
    :param rational1: The rational acting as `numerator.`
    :param rational2: The rational acting as `denominator.`

    Call :func:`__init__` with `rational0` as `numerator`
    and `rational1` / `rational2` as `denominator`."""
    __init__(rational0, rational1 / rational2)

@method(Rational, Decimal)
def __init__(rational, decimal):
    """Initialize the object from a :class:`decimal.Decimal`.
    :param rational: The rational number to be initialized.
    :param decimal: The decimal number the rational is initialized from.
    
    If the `decimal`'s exponent is negative compute a scaling
    denominator 10 ** -exponent and initialise `rational`
    with the decimal scaled by the denominator and the denominator.
    
    In the other case the `decimal` is simply converted to an
    `int` and used as numerator."""
    
    exponent = decimal.as_tuple().exponent
    if exponent < 0:
        denominator = Decimal((0, (1,), -exponent))
        __init__(rational,
                int(decimal * denominator),
                int(denominator))
    else:
        __init__(rational, int(decimal))


@method(Rational)
def __float__(rational):
    """Convert a rational to a float."""
    return float(rational.numerator) / float(rational.denominator)


@method(Rational, Writer)
def __out__(rational, writer):
    """Write a nice representation of the rational.
    
    Denominators that equal 1 are not printed."""
    writer("%d", rational.numerator)
    if rational.denominator != 1:
        writer(" / %d", rational.denominator)

@method(Rational, Writer)
def __spy__(rational, writer):
    """Write a debug representation of the rational."""
    writer("%s(", rational.__class__.__name__)
    if rational.numerator != 0:
            writer("%r", rational.numerator)
            if rational.denominator != 1:
                writer(", %r", rational.denominator)
    writer(")")


@method(Rational, Rational)
def __add__(a, b):
    """Add two rational numbers."""
    return Rational(a.numerator * b.denominator + b.numerator * a.denominator,
            a.denominator * b.denominator)

@method(object, Rational)
def __add__(a, b):
    """Add an object and a rational number.
    
    `a` is converted to a :class:`Rational` and then both are added."""
    return Rational(a) + b

@method(Rational, object)
def __add__(a, b):
    """Add a rational number and an object.

    `b` is converted to a :class:`Rational` and then both are added."""
    return a + Rational(b)


@method(Rational, Rational)
def __sub__(a, b):
    """Subtract two rational numbers."""
    return Rational(a.numerator * b.denominator - b.numerator * a.denominator,
            a.denominator * b.denominator)

@method(object, Rational)
def __sub__(a, b):
    """Subtract an object and a rational number.

    `a` is converted to a :class:`Rational` and then both are subtracted."""
    return Rational(a) - b

@method(Rational, object)
def __sub__(a, b):
    """Subtract a rational number and an object.

    `b` is converted to a :class:`Rational` and then both are subtracted."""
    return a - Rational(b)


@method(Rational, Rational)
def __mul__(a, b):
    """Multiply two rational numbers."""
    return Rational(a.numerator * b.numerator, a.denominator * b.denominator)

@method(object, Rational)
def __mul__(a, b):
    """Multiply an object and a rational number.

    `a` is converted to a :class:`Rational` and then both are multiplied."""
    return Rational(a) * b

@method(Rational, object)
def __mul__( a, b ):
    """Multiply a rational and an object.

    `b` is converted to a :class:`Rational` and then both are multiplied."""
    return a * Rational(b)


@method(Rational, Rational)
def __div__(a, b):
    """Divide two rational numbers."""
    return Rational(a.numerator * b.denominator, a.denominator * b.numerator)

@method(object, Rational)
def __div__(a, b):
    """Divide an object and a rational number.

    `a` is converted to a :class:`Rational` and then both are divided."""
    return Rational(a) / b

@method(Rational, object)
def __div__(a, b):
    """Divide a rational and an object.

    `b` is converted to a :class:`Rational` and then both are divided."""
    return a / Rational(b)


@method(Rational)
def __neg__(rational):
    """Negate a rational number."""
    return Rational(-rational.numerator, rational.denominator)


@method(Rational, Rational)
def __eq__(a, b):
    """Compare to rational numbers for equality."""
    return a.numerator == b.numerator and a.denominator == b.denominator

@method(Rational, object)
def __eq__(a, b):
    """Compare a rational numbers and another object for equality."""
    return a == Rational(b)

@method(Rational, int)
def __eq__(a, b):
    """Compare a rational numbers and an integer for equality.
    
    :Note: This is an optimisation for `int`."""
    return a.denominator == 1 and a.numerator == b

@method(Rational, long)
def __eq__(a, b):
    """Compare a rational numbers and a long for equality.
    
    :Note: This is an optimisation for `long`."""
    return a.denominator == 1 and a.numerator == b


@method(Rational, Rational)
def __ne__(a, b):
    """Compare to rational numbers for inequality."""
    return a.numerator != b.numerator or a.denominator != b.denominator

@method(Rational, object)
def __ne__(a, b):
    """Compare to rational numbers for inequality."""
    return a != Rational(b)


@method(Rational, Rational)
def __lt__(a, b):
    """Answer `True` if `a` is smaller than `b`."""
    return (b - a).numerator > 0

@method(Rational, object)
def __lt__(a, b):
    """Answer `True` if `a` is smaller than `b`."""
    return a < Rational(b)

@method(Rational, Rational)
def __le__(a, b):
    """Answer `True` if `a` is smaller than or equal `b`."""
    return (b - a).numerator >= 0

@method(Rational, object)
def __le__(a, b):
    """Answer `True` if `a` is smaller than or equal `b`."""
    return a <= Rational(b)



@method(Rational, Rational)
def __gt__(a, b):
    """Answer `True` if `a` is bigger than `b`."""
    return (a - b).numerator > 0

@method(Rational, object)
def __gt__(a, b):
    """Answer `True` if `a` is bigger than `b`."""
    return a > Rational(b)

@method(Rational, Rational)
def __ge__(a, b):
    """Answer `True` if `a` is bigger or equal than `b`."""
    return (a - b).numerator >= 0

@method(Rational, object)
def __ge__(a, b):
    """Answer `True` if `a` is bigger or equal than `b`."""
    return a >= Rational(b)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
