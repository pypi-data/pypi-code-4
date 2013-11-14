'''
qmpy.data.strings

Contains useful functions for string manipulation. Some important conventions
observed throughout qmpy that are particularly relevent here:
    names are of the form: is FeO2 Ni3B
    formula are of the form: Fe,O2 Ni3,B
    comp are of the form: {'Fe':1, 'O':2} {'Ni':3, 'B':1}
    latex are of the form: FeO_2 Ni_3B

These forms can be converted between with x_to_y functions, where x can be
name, formula, comp or latex. (latex and only be y)

'''
from collections import defaultdict
import itertools
import numpy as np
import re
import yaml
import fractions as frac
import decimal as dec

from qmpy.utils.math import *
from qmpy.data import elements, element_groups

## regex's
re_comp = re.compile('({[^}]*}[,0-9x\.]*|[A-Z][a-wyz]?)([,0-9x\.]*)')
spec_comp = re.compile('([A-Z][a-z]?)([0-9\.]*)([+-]?)')

## Parsing

def parse_comp(value):
    comp = {}
    for elt, amt in re_comp.findall(value):
        if elt in ['D', 'T']:
            elt = 'H'
        if amt == '':
            comp[elt] = 1
        elif is_integer(amt):
            comp[elt] = int(amt)
        else:
            comp[elt] = float(amt)
    return comp

def parse_sitesym(sitesym, sep=','):
    rot = np.zeros((3, 3), dtype='int')
    trans = np.zeros(3)
    for i, s in enumerate (sitesym.split(sep)):
        s = s.lower().strip()
        while s:
            sign = 1
            if s[0] in '+-':
                if s[0] == '-':
                    sign = -1
                s = s[1:]
            if s[0] in 'xyz':
                j = ord(s[0]) - ord('x')
                rot[i, j] = sign
                s = s[1:]
            elif s[0].isdigit() or s[0] == '.':
                n = 0
                while n < len(s) and (s[n].isdigit() or s[n] in '/.'):
                    n += 1
                t = s[:n]
                s = s[n:]
                trans[i] = float(frac.Fraction(t))
            else:
                raise ValueError('Failed to parse symmetry of %s' % (sitesym))
    return rot, trans

def parse_species(value):
    elt, charge, sign = spec_comp.findall(value)[0]
    if charge == '':
        return elt, None
    elif is_integer(charge):
        charge = int(charge)
    else:
        charge = float(charge)

    if sign in ['+', '']:
        return elt, charge
    elif sign == '-':
        return elt, -1*charge

## Formatting

def format_species(element, value):
    if value is None:
        return element
    if is_integer(value):
        ox = str(abs(int(value)))
    else:
        ox = str(abs(float(value))).rstrip('0.')
    name = '%s%s' % (element, ox)
    if value < 0:
        name += '-'
    else:
        name += '+'
    return name

def get_coeffs(values):
    wasdict = False
    if isinstance(values, dict):
        keys, values = zip(*values.items())
        wasdict = True

    coeffs = []
    for v in values:
        if v == 1:
            coeffs.append('')
        elif is_integer(v):
            coeffs.append('%d' % v)
        else:
            coeffs.append(('%.8f' % v).rstrip('0'))

    if wasdict:
        return dict(zip(keys, coeffs))
    else:
        return coeffs

def electronegativity(elt):
    if not elt in elements:
        return 0.0
    else:
        if not 'electronegativity' in elements[elt]:
            return 0.0
        return elements[elt]['electronegativity']

def format_comp(comp, template='{elt}{amt}', join=''):
    elts = sorted(comp.keys(), key=lambda x: electronegativity(x))
    coeffs = get_coeffs(comp)
    return ''.join(template.format(elt=k, amt=coeffs[k]) for k in elts)

def html_comp(comp):
    return format_comp(comp, template='{elt}<sub>{amt}</sub>')

def latex_comp(comp):
    return format_comp(comp, template='{elt}_{{{amt}}}')

def unit_comp(comp):
    tot = float(sum(comp.values()))
    return dict( (k, v/tot) for k, v in comp.items())

def reduce_comp(values):
    '''
    Attempt to construct a 'pretty' composition string. NOTE: Any composition
    within between n-0.05 and n+0.05 will be rounded to n.
    
    Tries 3 options:
        a) Find the greatest common denominator for all coefficients.

        b) If that fails (i.e. the GCD < 1e-10, and there is no accurate
        rational value ), try multiplying the coefficients by the first 20
        prime numbers. For example: if your coefficients are 
        [0.3333333, 0.6666667], this will fail to identify a rational GCD, but
        if you multiply by 3, you get [1, 2]. NOTE: This only works because we
        only keep compositions to 1 decimal place. As a result, 0.6666667
        cannot be properly identified, but 0.6666667*3, can. In fact, [ 0.33,
        0.67 

        c) If None of these work, simply return the literal composition given,
        rounded to 3 decimal places.
    '''

    wasdict = False
    if isinstance(values, dict):
        keys, values = zip(*values.items())
        wasdict = True

    def roundclose(v):
        if is_integer(v, tol=5e-2):
            return int(round(v))
        else:
            return v
    i = 0
    d = 0
    vals = np.array([ roundclose(v) for v in values])
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    while d < 1e-6:
        if i > len(primes)-1:
            vals = np.round(vals*10**3)/10**3
            break
        i += 1
        p = primes[i-1]
        d = reduce(frac.gcd, [ roundclose(v) for v in vals*p ])
    else:
        vals = np.round(vals*p/d)

    if wasdict:
        return dict(zip(keys, vals))
    else:
        return vals.tolist()

def normalize_comp(values):
    wasdict = False
    if isinstance(values, dict):
        keys, values = zip(*values.items())
        wasdict = True

    vals = np.array(values)
    vals /= min(vals)

    if wasdict:
        return dict(zip(keys, vals))
    else:
        return vals.tolist()

def parse_formula_regex(formula):
    '''Take in a generalized expression for a composition. Use symbols for
    groups of elements for combinatorial replacements.

    Groups of elements can be identified by:
        - valence shell: 3d, 5s, 2p, etc...
        - group: G1 (alkali), G17 (halides), G4 (2d2), etc...
        - row: R1, R3
        - block: DD (all d-block), PP (all p-block), etc...

    Examples:
    >>> parse_formula_regex('Fe2O3')
    [{'Fe':2, 'O':3}]
    >>> parse_formula_regex('{Fe,Ni}2O3')
    [{'Fe':2, 'O':3}, {'Ni':2, 'O':3}]
    >>> parse_formula_regex('{3d}2O3')
    [{'Co': 2.0, 'O': 3.0}, {'Cr': 2.0, 'O': 3.0}, {'Cu': 2.0, 'O':3.0}, 
    {'Fe': 2.0, 'O': 3.0}, {'Mn': 2.0, 'O': 3.0}, {'Ni': 2.0, 'O': 3.0},
    {'Sc': 2.0, 'O': 3.0}, {'O': 3.0, 'Ti': 2.0}, {'O': 3.0, 'V': 2.0}, 
    {'Zn':2.0, 'O': 3.0}]

    '''
    formulae = []
    sfind = re.compile('({[^}]*}[,0-9x\.]*|[A-Z][a-wyz]?[,0-9x\.]*)')
    matches = sfind.findall(formula)
    for term in matches:
        if '{' in term:
            symbols, amt = term.replace('{','').split('}')
            symbols = symbols.split(',')
            elts = []
            for symbol in symbols:
                if symbol in element_groups.keys():
                    elts += [ e for e in element_groups[symbol] ]
                else:
                    elts += [ symbol ]
            formulae.append([ e+amt for e in elts ])
        else:
            formulae.append([term])
    return [ parse_comp(''.join(ref)) for ref in itertools.product(*formulae) ]
