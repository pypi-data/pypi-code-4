'''
Implementation of the Bond-Valence Sum method.

Data sourced from: 
    http://www.iucr.org/resources/data/datasets/bond-valence-parameters
'''

import numpy as np

#from qmpy.data.bond_valence import bond_valence_parameters
#from qmpy.data.bond_valence import bond_valence_references

def param_getter(symbol1, symbol2):
    pair = set([ symbol1, symbol2])
    #results = []
    for data in bond_valence_parameters:
        if set([data['A_species'], data['B_species']]) == pair:
            #results.append(data)
            return data
    #return results

def v_ij(atom1, atom2, params=None):
    if params is None:
        params = param_getter(atom1.element_id, atom2.element_id)
    if params is None:
        return None
    R = atom1.structure.get_distance(atom1, atom2)
    R0 = params['param_r0']
    B = params['param_B']
    return np.exp( (R0 - R)/B )

def valence_sum(atom):
    valence = 0
    structure = atom.structure
    for atomp in structure.atoms:
        if atomp is atom:
            pass
        elif structure.get_distance(atom, atomp) < 2.5:
            v = v_ij(atom, atomp)
            if v is None:
                continue
            valence += v
    return valence

def total_valence_sum(structure):
    for atom in structure.atoms:
        atom.charge = valence_sum(atom)
