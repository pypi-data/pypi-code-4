"""calculate moleweight from chemical composition or structure formula

This module provides the following functions:
- moleweight(string | cdict): interface function which can be given a structure
        string, composition string or composition dictionary and returns the
        molecular weight. This is the function a user will normally call.
- compare_composition(m1, m2): test if the molecular composition of two
        molecules is equal. Arguments can be structure or composition strings
        or composition dictionaries
- composition_from_structure(structure): converts a structure string (see below)
        into a composition string or dictionary
- moleweight_from_composition(cstring | cdict): computes the molecular weight
        of a molecule from its composition string or composition dictionary
- cstring_to_cdict(cstring): converts a composition string to a dictionary
- cdict_to_string(cdict): converts a composition dictionary to a string,
        optionally with Latex-style subscripts

Definitions:
- a composition string is a string of the form M1[N1][M2[N2]]..., where
        Mi denotes a one or two-letter element name (first letter must be
        upper case, possible second letter lowercase), and Ni denotes the
        multiplicity. Although uncommon in practice, element names may be
        duplicated.
        Examples: 'C', 'H2O', 'C2H5O2', 'CH3SCH3', 'NaCl'
- a composition dictionary contains all elements of a molecule as keys and
        the element counter (multiplicity) as values.
        Examples: 'CO2' would yield { 'C':1, 'O':2 }
- a structure string extends the syntax of a composition string to include
        groups (e.g. '(CH3)') and the option to mark single bonds ('-'),
        double bonds ('='), and triple bonds ('#'). Groups may again have
        multipliers (e.g. '(CH3)2') and may be nested.
        Examples: 'CH3CH(O)OOH', 'CH2=CH2', 'CH2(CHO)2'

Limitations:
- this program does not understand SMILES or InChi notation
- this program does not support isotopes

ToDo:
- add a check for validity of a structure string (?)
"""

# Martin Schultz, FZ Juelich, 2013-09-19, V1.1
# - revised interface and extended functionality to allow for bond notation

# data: atomic weights
mw = {}
mw['e']  = 5.485799e-4
mw['H']  = 1.0074
mw['He'] = 4.0020602
mw['Li'] = 6.941
mw['Be'] = 9.012182
mw['B']  = 10.811
mw['C']  = 12.011
mw['N']  = 14.00674
mw['O']  = 15.9994
mw['F']  = 18.9984032
mw['Ne'] = 20.1797
mw['Na'] = 22.989768
mw['Mg'] = 24.305
mw['Al'] = 26.981539
mw['Si'] = 28.0855
mw['P']  = 30.97362
mw['S']  = 32.066
mw['Cl'] = 35.4527
mw['Ar'] = 39.948
mw['K']  = 39.0983
mw['Ca'] = 40.078
mw['Sc'] = 44.95591
mw['Ti'] = 47.867
mw['V']  = 50.9415
mw['Cr'] = 51.9961
mw['Mn'] = 54.93085
mw['Fe'] = 55.845
mw['Co'] = 58.9332
mw['Ni'] = 58.6934
mw['Cu'] = 63.546
mw['Zn'] = 65.39
mw['Ga'] = 69.723
mw['Ge'] = 72.61
mw['As'] = 74.92159
mw['Se'] = 78.96
mw['Br'] = 79.904
mw['Kr'] = 83.8
mw['Rb'] = 85.4678
mw['Sr'] = 87.62
mw['Y']  = 88.90585
mw['Zr'] = 91.224
mw['Nb'] = 92.90638
mw['Mo'] = 95.94
mw['Tc'] = 98.
mw['Ru'] = 101.07
mw['Rh'] = 102.9055
mw['Pd'] = 106.42
mw['Ag'] = 107.8682
mw['Cd'] = 112.411
mw['In'] = 114.818
mw['Sn'] = 118.71
mw['Sb'] = 121.76
mw['Te'] = 127.6
mw['I']  = 126.90447
mw['Xe'] = 131.29
mw['Cs'] = 132.90543
mw['Ba'] = 137.327
mw['La'] = 138.9055
mw['Hf'] = 178.49
mw['Ta'] = 180.9479
mw['W']  = 183.84
mw['Re'] = 186.207
mw['Os'] = 190.23
mw['Ir'] = 192.217
mw['Pt'] = 195.08
mw['Au'] = 196.96654
mw['Hg'] = 200.59
mw['Tl'] = 204.3833
mw['Pb'] = 207.2
mw['Bi'] = 208.98037
mw['Po'] = 209.
mw['At'] = 210.
mw['Rn'] = 222.
mw['Fr'] = 223.
mw['Ra'] = 226.025
mw['Ac'] = 227.028


def cdict_to_string(cdict, latex=False, ones=False):
    """Converts a dictionary of elemental composition into a molecular
    formula.
    Latex-style subscripting will be used if the latex-keyword is True.
    Use the ones keyword to explicitly include multiplicities of 1 (e.g. 'C1O1').
    No error checking: we assume that all element names are correct."""
    def format_one(k, v, latex=False, ones=False):
        m = k
        if ones or v > 1:
            if latex:
                m += "_%i" % (v)
###             m += "_{%i}" % (v)
            else:
                m += "%i" % (v)
        return m
    
    res = ""
    # respect general order of organic molecules: C, H, N, O
    order = ["Hg", "C", "H", "S", "F", "Cl", "Br", "I", "N", "O"]
    for el in order:
        if el in cdict:
            res += format_one(el, cdict[el], latex, ones)
    # now go through remaining elements
    for k in cdict:
        if not k in order:
            res += format_one(k, cdict[k], latex, ones)
    return res
    

def cstring_to_cdict(cstring, cdict=None):
    """Converts a composition string to a dictionary of elemental
    composition. The element names are the keys, the multiplicity the values
    of the dictionary.
    If you pass a valid cdict as second argument, elements and multipliers
    will be added.
    The function checks if element names are contained in the mw dictionary."""
    def add_to_dict(cdict, el, count):
        if not el in mw.keys():
            raise ValueError("Invalid element %s in composition string %s!" % (el, cstring))
        if el in cdict.keys():
            cdict[el] += count
        else:
            cdict[el] = count

    if cdict is None:
        cdict = {}
    wasUpper = False
    wasNumber = False
    validU = "ABCDFHIKLMNOPRSTUVWXYZ"   # first letters of chemical elements
    validL = "abcdefghilnorstu"   # second letter of chemical elements
    validN = "0123456789"  # multiplier
    # special case "e" for electron
    if cstring.startswith("e"):
        add_to_dict(cdict, "e", 1)    # only one allowed
    else:
        el = ""
        count = 0
        for c in cstring:
            if not (c in validU or c in validL or c in validN):
                raise ValueError("Invalid character (%s) in composition string %s"%(c, cstring))
            if wasUpper:       # test for two-letter species e.g. Cl
                if c in validL:
                    el += c
                elif c in validN:
                    if wasNumber:  # next digit of multiplier
                        count = count*10 + int(c)
                    else:
                        count = int(c)
                    wasNumber = True
            if c in validU:     # new atom
                if wasUpper:    # finished analysis of previous compound
                    add_to_dict(cdict, el, count)
                wasUpper = True
                wasNumber = False
                el = c
                count = 1
        if wasUpper:    # finished analysis of final compound
            add_to_dict(cdict, el, count)
    return cdict


def moleweight_from_composition(arg):
    """Takes either a composition string or composition dictionary as
    argument and calculates the molecular weight of the molecule"""
    if isinstance(arg, basestring):
        cdict = cstring_to_cdict(arg)
    else:
        cdict = arg
    res = 0.
    for k, v in cdict.items():
        res += v * mw[k]
    return res


def composition_from_structure(structure, asstring=False, **kwargs):
    """Converts a structure string into a composition dictionary or string
    kwargs can be provided to determine the look of the string if asstring
    is True. Valid kwargs are latex and ones (see cdict_to_cstring)."""
    def merge_cdicts(cdict1, cdict2):
        """combine information of two composition dictionaries
        cdict1 will be modified"""
        for k, v in cdict2.items():
            if k in cdict1:
                cdict1[k] += v
            else:
                cdict1[k] = v
        return cdict1
    
    def parse(s, niter=1):
        """parse a (sub)string
        niter keyword is for debugging purposes"""
        p0 = p1 = 0
        mult = 1
        cdict = {}
        while (p0 < len(s)):
            pp = s.find("(", p0)    # group start
            if pp < 0:              # no groups left
                csub = cstring_to_cdict(s[p0:])
                cdict = merge_cdicts(cdict, csub)
                p0 = len(s)         # done
            else:
                # parse structure part in front of next group
                if pp > p0:
                    csub = parse(s[p0:pp], niter=niter+1)
                    cdict = merge_cdicts(cdict, csub)
                p0 = pp
                # find end of group
                p1 = p0 + 1
                pc = 1     # parantheses counter
                while (pc > 0 and p1 < len(s)):
                    if s[p1] == ")":
                        pc -= 1
                    elif s[p1] == "(":
                        pc += 1
                    p1 += 1
                if pc > 0:
                    raise ValueError("Unmatched parantheses in %s!" % (structure))
                # parse group substring
                csub = parse(s[p0+1:p1-1], niter=niter+1)
                # extract group multiplier if present
                validN = "0123456789"
                p0 = p1
                while (p1 < len(s) and s[p1] in validN):
                    p1 += 1
                if p1 > p0:          # found a multiplier
                    mult = int(s[p0:p1])
                    for k in csub:
                        csub[k] *= mult  # apply to element count
                # add elements of sub-structure to result
                cdict = merge_cdicts(cdict, csub)
                p0 = p1
        return cdict
                
    # eliminate decorative characters
    decoration = "-=#."
    tmp = structure.strip()
    for c in decoration:
        tmp = tmp.replace(c, "")
    # now we should only have (possibly nested) groups of composition strings
    # look for '(...)N'
    res = parse(tmp)
    if asstring:
        res = cdict_to_string(res, **kwargs)
    return res


def compare_composition(m1, m2, verbose=False):
    """Compare the composition of two molecules
    Returns True if both consist of the same elements, False otherwise
    If verbose is True, deviations will be reported"""
    # convert both "molecules" to a composition dictionary
    if isinstance(m1, basestring):
        cdict1 = composition_from_structure(m1)
    else:
        cdict1 = m1
    if isinstance(m2, basestring):
        cdict2 = composition_from_structure(m2)
    else:
        cdict2 = m2
    res = True
    # first loop with cdict1 as reference
    for k, v in cdict1.items():
        if not k in cdict2:
            res = False
            if verbose:
                print "Element %s not in second molecule." % (k)
        else:
            if cdict2[k] != v:
                res = False
                if verbose:
                    print "Multiplicity of element %s differs: %i vs %i." % (k, v, cdict2[k])
    # second loop with cdict2 as reference (only missing elements)
    for k, v in cdict2.items():
        if not k in cdict1:
            res = False
            if verbose:
                print "Element %s not in first molecule." % (k)
    if res and verbose:
        print "The composition of both molecules is equal."
    return res


def moleweight(molecule):
    """calculate moleweight of a molecule"""
    if isinstance(molecule, basestring):
        cdict = composition_from_structure(molecule)
    else:
        cdict = molecule   # we assume that anything other than string is a valid composition dictionary
    return moleweight_from_composition(cdict)

    

def test_moleweight():
    from numpy.testing import assert_almost_equal
    valid = [ ('C', 12.011 ),
              ('N2', 28.01348 ),
              ('O3', 47.9982),
              ('N2O', 44.01288),
              ('Cl2O2', 102.9042),
              ('BrCl', 115.3567),
              ('CH3C(O)O2', 75.0424),
              ('(CHO)2', 58.03560),
              ('(HO)(CH2)2CH(CH3)2', 88.1432), # 3-methyl-1-butanol from MCM
              ('H', 1.0074),
              ('Hg', 200.59),
              ('CH2=CH2', 28.05160),   # double bond
              ('HC#N', 27.02514),  # triple bond
              ('CH3-C(=O)-CH3', 58.07680) ] 
    for v, expected in valid:
        answer = moleweight(v)
        print "%40s : %12.5f" % (v, answer)
        assert_almost_equal(answer, expected)

        
