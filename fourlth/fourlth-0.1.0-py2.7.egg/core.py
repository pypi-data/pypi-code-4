"""\
Core "words" for FourlthInterpreter class
"""

import logging
log = logging.getLogger(__name__)

import math

def dup(stk):
    """duplicate top element on stack  ( x -- x x )"""
    top = stk.pop()
    stk.push(top)
    stk.push(top)
    return None

def nzdup(stk):
    """duplicate top element on stack if it is non-zero  ( x -- x [ x ] )"""
    top = stk.pop()
    stk.push(top)
    if top != 0:  stk.push(top)
    return None

def test_stack(stk):
    """push 1 if stack is empty else push zero  ( -- 1 | 0 )"""
    stk.push(1 if len(stk) == 0 else 0)
    return None

def top(stk):
    """return a copy of top of stack.  stack is left unchanged  ( x -- x )"""
    top = stk.po()
    stk.push(top)
    return top

def drop(stk):
    """pops the top element, discarding it ( x -- )"""
    stk.pop()
    return None

def swap(stk):
    """swap top two stack elements  ( x  y -- y  x )"""
    stk.swap()
    return None

def rot(stk):
    """rotate the top three elements of the stack  ( x y z -- z x y )"""
    stk.rot()

def over(stk):
    """push copy of next-to-top element  ( x y z --- x y z y """
    stk.over()

def tuck(stk):
    """insert copy of top element just under next-to-last element  ( x y z -- x z y z )"""
    stk.tuck()

def pick(stk):
    """push a copy of nth element where ``n`` is value at top-of-stack  ( x y z 2 -- x y z x )
observe that ``0 PICK`` is functionally identical to ``DUP``
and ``1 PICK`` is synonymous with ``OVER``.
"""
    stk.pick()

def roll(stk):
    """remove the nth element down in the stack and push it  ( u v x y z 3 -- u x y z v )
observe that ``1 ROLL`` is the same as ``SWAP`` and ``2 ROLL`` is the same as ``ROT``.
"""
    stk.roll()

def dot(stk):
    """print top of stack  ( xx -- )"""
    print stk.pop(),

def cr(stk):
    """emit a newline  ( -- )"""
    print

def add(stk):
    """add top to elements of stack, pusing result  ( x y -- x+y )"""
    return stk.pop() + stk.pop()

def subtract(stk):
    """subtract top element from element just beneath it, pushing result   ( x y -- x-y)"""
    subtrahend = stk.pop()
    return stk.pop() - subtrahend

def multiply(stk):
    """multiply top two elements, pushing result  ( x y -- x*y )"""
    return stk.pop() * stk.pop()

def divide(stk):
    """\
divide next-to-top of stack by top-of-stack, pushing result  ( x y -- x / y)
throws *FourlthRuntimeError* if y == 0
"""
    denom = stk.pop()

    if denom == 0: raise FourlthRuntimeError('divide by zero')

    return stk.pop() / denom


def modulo(stk):
    """modulo of next-to-top with top  ( x  y -- x%y )"""
    modulus = stk.pop()
    return stk.pop() % modulus

def pow(stk):
    """next-to-top raised to <top> power  ( x  y -- pow(x,y) )"""
    exp = stk.pop()
    return math.pow(stk.pop(), exp)
    
def tofloat(stk):
    """convert top element to type *float* if possible.  throws *FourlthRuntimeError* of element is not convertible."""
    try:
        number = stk.pop()
        return float(number)
    except ValueError:
        raise FourlthRuntimeError('cannot convert "{0}" to float'.format(number))
        

def toint(stk):
    """convert top element to type *int* if possible.  throws *FourlthRuntimeError* of element is not convertible."""
    try:
        number = stk.pop()
        return int(number)
    except ValueError:
        raise FourlthRuntimeError('cannot convert "{0}" to int'.format(number))

def eq(stk):
    """pushes 1 if top two elements are equal, zero otherwise"""
    stk.push(1 if stk.pop() == stk.pop() else 0)
    
def ne(stk):
    """pushes 1 if top two elements are unequal, zero otherwise"""
    stk.push(1 if stk.pop() != stk.pop() else 0)
    
def lt(stk):
    """pushes 1 if next-to-last element is less than top element, zero otherwise"""
    n2, n1 = stk.pop(), stk.pop()
    stk.push(1 if n1 < n2 else 0)

def le(stk):
    """pushes 1 if next-to-last element is less than or equal to top element, zero otherwise"""
    n2, n1 = stk.pop(), stk.pop()
    stk.push(1 if n1 <= n2 else 0)

def gt(stk):
    """pushes 1 if next-to-last element is greater than top element, zero otherwise"""
    n2, n1 = stk.pop(), stk.pop()
    stk.push(1 if n1 > n2 else 0)

def ge(stk):
    """pushes 1 if next-to-last element is greater than or equal to top element, zero otherwise"""
    n2, n1 = stk.pop(), stk.pop()
    stk.push(1 if n1 >= n2 else 0)

def logical_not(stk):
    """logical negation : push 1 if top of stack is zero, otherwise push zero"""
    stk.push(1 if stk.pop() == 0 else 0)

def logical_or(stk, invert=False):
    """if either of the top two elements are non-zero, push 1.  IF both are zero, push zero."""
    result = 1 if (stk.pop() != 0 or stk.pop() != 0) else 0
    stk.push(int(not result if invert else result))

def logical_and(stk, invert=False):
    """if either of the top elements are zero, push zero.  If both are non-zero, push 1."""
    result = 1 if (stk.pop() != 0 and stk.pop() != 0) else 0
    stk.push(int(not result if invert else result))

def iszero(stk, invert=False):
    """push 1 if top of stack is zero, otherwise push zero
(If ``invert=True`` then push 0 if top of stack is zero, otherwise push 1.)
"""
    stk.push(1 if stk.pop() == 0 else 0)

def isneg(stk):
    """push 1 if top of stack < 0, otherwise push zero."""
    stk.push(1 if stk.pop() < 0 else 0)

def ispos(stk):
    """push 1 if top of stack > 0, otherwise push zero."""
    stk.push(1 if stk.pop() > 0 else 0)

def store(stk):
    """Store the next-to-last value on the stack in a location named by the top element of the stack."""
    try:
        key = stk.pop()
        stk.dictionary['VARIABLES'][key] = stk.pop()
        log.debug('storing: {0} <- {1}'.format(key, stk.dictionary['VARIABLES'][key]))
        return None
    except IndexError:
        raise FourlthRuntimeError('stack empty')

        
def fetch(stk):
    """Retrieve the value found at the location named by the top of the stack and push the value.
This throws *FourlthRuntimeError* if there is no such (named) location."""
    try:
        key = stk.pop()
        log.debug('fetching "{0}"'.format(key))
        stk.push(stk.dictionary['VARIABLES'][key])
        return None
    except KeyError:
        raise FourlthRuntimeError('no such variable "{0}"'.format(key))

def fetch_dot(stk):
    """shorthand function since fetch is often followed by a dot (display top of stack)."""
    try:
        key = stk.pop()
        log.debug('fetching "{0}"'.format(key))
        print stk.dictionary['VARIABLES'][key],
        return None
    except KeyError:
        raise FourlthRuntimeError('no such variable "{0}"'.format(key))

def tolist(stk):
    """Construct a list comprised of all the current elements of the stack.  Push this
list onto the stack.  (  x y z -- [ x, y, z ] ).
"""
    result = list()
    while True:
        try:
            result.append(stk.pop())
        except IndexError:
            stk.push(result)
            log.debug('LIST: {0}'.format(result))
            return None

def split_list(stk):
    """inverse of ``tolist``.  assumes top element is a list, breaks it up into
individual elements, pushing each on the stack.  ( [ x, y, z ] -- x y z )
"""
    try:
        lst = stk.pop()
        for e in lst: stk.push(e)
        return None

    except IndexError:
        raise FourlthRuntimeError('stack empty')

    except TypeError:
        raise FourlthRuntimeError('not a list')

    except:  # Everything else
        FourlthRuntimeError(sys.exc_info()[1])

    log.error('should never get here')
    return None  
    

# Core "words" that are mapped to the foregoing functions.
    
base_dictionary = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '/': divide,
    'div': divide,
    '%': modulo,
    '**': pow,
    '=': eq,
    '!=': ne,
    '>': gt,
    '>=': ge,
    '<': lt,
    '<=': le,
    '0=': iszero,
    '0<': isneg,
    '0>': ispos,
    '.': dot,
    'DOT': dot,
    '!': store,
    '@': fetch,
    '?': fetch_dot,
    'DOT': dot,  # Dot doesn't work in URLs
    'AND': logical_and,
    'CR': cr,
    'I': lambda x: x.push(x.index[0]),
    'J': lambda x: x.push(x.index[1]),
    'OR': logical_or,
    'NAND': lambda x: logical_and(x, invert=True),
    'NOR': lambda x: logical_or(x, invert=True),
    'DROP': drop,
    'DUP': dup,
    '?DUP': nzdup,
    'INT': toint,
    'FLOAT': tofloat,
    'LIST': tolist,
    'OVER': over,
    'PICK': pick,
    'ROLL': roll,
    'SPLIT': split_list,
    'TUCK': tuck,
    'ROT': rot,
    '?STACK': test_stack,
    'SWAP': swap,
    'TOP': top,
    }
