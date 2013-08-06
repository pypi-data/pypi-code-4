from collections import defaultdict
import itertools
import numpy as np
import re
from qmpy.element import *
from my_math import *

'''
A 'formula' or 'name' is FeO2, Ni3B, etc...
A 'composition' or 'comp' is {'Fe':1, 'O':2}, {'Ni":3, 'B':1}, etc...
'''

sfind = re.compile('[A-Z][a-wyz]?[0-9\.x]*')
#TODO
#   - fix parse_formula

def stupid_order(elt):
    if elt == 'O':
        return 'zzzzzz'
    elif elt in [ 'F', 'Br', 'Cl', 'I' ]:
        return 'zzzzz'
    elif elt == 'H':
        return 'zzzz'
    elif elt in [ 'P', 'S', 'N', 'C', 'B', 'Si' ]:
        return 'zzz'+elt
    elif elt in [ 'Li', 'Na', 'K', 'Rb', 'Cs' ]:
        return 'AAA'+elt
    elif elt in ['Be', 'Mg', 'Ca', 'Sr', 'Ba']:
        return 'AA'+elt
    else:
        return elt

def comp_to_latex(comp, special='reduce'):
    if special=='reduce':
        divisor = get_gcd(comp.values())
        comp = dict((k,v/divisor) for k,v in comp.items())
    name = ""
    for key in sorted(comp.keys(), key=lambda x: stupid_order(x)):
        if comp[key] == 1:
            n = ""
        else:
            if comp[key]:
                n = '_{%s}' % int(comp[key])
        name += key+n
    if name == 'LiHO':
        name = 'LiOH'
    return name

def comp_to_name(comp, special=None):
    if special=='reduce':
        divisor = get_gcd(comp.values())
        comp = dict((k,v/divisor) for k,v in comp.items())
    name = ""
    for key in sorted(comp.keys()):
        if comp[key] == 1:
            n = ""
        else:
            n = str(int(comp[key]))
        name += key+n
    if name == 'LiHO':
        name = 'LiOH'
    return name

def comp_to_formula(comp, special=None):
    if special=='reduce':
        divisor = get_gcd(comp.values())
        comp = dict((k,v/divisor) for k,v in comp.items())
    name = ""
    for key in sorted(comp.keys()):
        name += '%s%s,' % (key, int(comp[key]))
    name = name.strip(',')
    return name

def name_to_comp(name, special=None):
    comp = defaultdict(float)
    for elt in sfind.findall(name):
        e = ''
        n = ''
        for char in elt:
            if char.isalpha():
                if char == 'x':
                    n = 0
                else:
                    e += char
            else:
                n += char
        if n == '': 
            n = 1
        if e == 'D' or e == 'T':
            e = 'H'
        comp[e] = float(n)
    divisor = 1.
    if special == 'reduce':
        divisor = get_gcd(comp.values())
    if special == 'unit':
        divisor = sum(comp.values())
    return defaultdict(float, dict((k,v/divisor) for k, v in comp.items()))

def parse_formula(formula):
    formulae = []
    sfind = re.compile('({[^}]*}[:0-9x\.]*|[A-Z][a-wyz]?[:0-9x\.]*)')
    matches = sfind.findall(formula)
    for term in matches:
        if '{' in term:
            symbols, amt = term.replace('{','').split('}')
            symbols = symbols.split(':')
            elts = []
            for symbol in symbols:
                if ElementSet.objects.filter(name=symbol).exists():
                    eset = ElementSet.objects.get(name=symbol)
                    elts += [ e.symbol for e in eset.elements.all()]
                else:
                    elts += [ symbol ]
            formulae.append([ e+amt for e in elts ])
        else:
            formulae.append([term])
    return [ name_to_comp(''.join(ref)) for ref in itertools.product(*formulae) ]
