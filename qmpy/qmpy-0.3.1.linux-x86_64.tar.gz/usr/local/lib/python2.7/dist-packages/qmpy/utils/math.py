'''qmpy.utils.math

Some mathematical functions which are used periodically.

'''
import numpy as np
from numpy.linalg import norm

def _gcd(a,b):
    '''
    Returns greatest common denominator of two numbers.
    
    Example:
    >>> _gcd(4, 6)
    2
    '''
    while b:
        a,b=b,a%b
    return a

def gcd(numbers):
    '''
    Returns greatest common denominator of an iterator of numbers.

    Example:
    >>> gcd(12, 20, 32)
    4
    '''
    numbers = list(numbers)
    if len(numbers) == 1:
        return numbers[0]
    a=numbers.pop()
    b=numbers.pop()
    tmp_gcd = _gcd(a,b)
    while numbers:
        tmp_gcd = _gcd(tmp_gcd,numbers.pop())
    return tmp_gcd

def is_integer(number, tol=1e-5):
    number = float(number)
    return abs(round(number) - number) < tol
        

def lcm(a,b):
    '''
    Returns least common multiple of two numbers.

    Example:
    >>> lcm(20,10)
    20
    '''
    return a*b/gcd(a,b)

def ffloat(string):
    '''
    In case of fortran digits overflowing and returing ********* this
    fuction will replace such values with 1e9
    '''

    try:
        new_float = float(string)
    except ValueError:
        if '*******' in string:
            new_float = 1e9
        else:
            print string
            return None
    return new_float

def angle(x, y):
    '''Return the angle between two lattice vectors

    Example:

    >>> angle([1,0,0], [0,1,0])
    90.0
    '''
    return np.arccos(np.dot(x,y)/(norm(x)*norm(y)))*180./np.pi

def basis_to_latparams(basis):
    """Returns the lattice parameters [a, b, c, alpha, beta, gamma].
    
    Example:
        
    >>> basis_to_latparams([[3,0,0],[0,3,0],[0,0,5]])
    [3, 3, 5, 90, 90, 90]
    """

    va, vb, vc = basis
    a = np.linalg.norm(va)
    b = np.linalg.norm(vb)
    c = np.linalg.norm(vc)
    alpha = angle(vb, vc)
    beta = angle(vc, va)
    gamma = angle(va, vb)
    return [a, b, c, alpha, beta, gamma]


def latparams_to_basis(latparam, units='degrees'):
    '''Convert a 3x3 basis matrix from the lattice parameters.

    Example:
    >>> latparams_to_basis([3, 3, 5, 90, 90, 90])
    [[3,0,0],[0,3,0],[0,0,5]]

    '''
    basis = []
    a, b, c = latparam[0:3]
    alpha, beta, gamma = latparam[3:6]

    if units == 'degrees':
        # need to convert to radians
        alpha *= np.pi/180
        beta *= np.pi/180
        gamma *= np.pi/180

    basis.append([a, 0, 0])
    basis.append([b*np.cos(gamma), b*np.sin(gamma), 0 ])
    cx = np.cos(beta)
    cy = (np.cos(alpha) - np.cos(beta)*np.cos(gamma))/np.sin(gamma)
    cz = np.sqrt(1. - cx*cx - cy*cy)
    basis.append([c*cx, c*cy, c*cz])
    basis = np.array(basis)
    basis[abs(basis) < 1e-10] = 0
    return basis

def coord_to_bin(coord):
    '''Convert a binary composition to an x-coordinate value:
    returns ( A )
    
    '''
    return coords[0]

def coord_to_gtri(coord):
    '''Convert a ternary composition to an x,y-coordinate pair:
    ( A+B/2, B*3^(1/2)/2 )
    
    '''
    return (coord[0] + coord[1]/2., 
            coord[1]*np.sqrt(3)/2)

def coord_to_gtet(coord):
    '''Convert a quaternary composition to an x,y,z triplet:
    ( A/2+B+C/2, A*3^(1/2)/2 + C*3^(1/2)/6, C*(2/3)^(1/2) )
    
    '''
    return (coord[0]/2 + coord[1] + coord[2]/2,
        coord[0]*np.sqrt(3)/2 + coord[2]*np.sqrt(3)/6.,
        coord[2]*np.sqrt(2./3))

def triple_prod(matrix):
    return np.dot(matrix[0], np.cross(matrix[1], matrix[2]))

def intervals(*args):
    for i in range(len(args)-1):
        print args[i+1] - args[i],
