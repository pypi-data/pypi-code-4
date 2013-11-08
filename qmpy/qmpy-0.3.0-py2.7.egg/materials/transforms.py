import numpy as np
from qmpy.utils import *
from composition import Composition

def strain(x1, x2=None, x3=None):
    raise NotImplementedError

def shear():
    raise NotImplementedError

def displace_atom():
    raise NotImplementedError

def joggle_atoms(structure):
    raise NotImplementedError

def replace(structure, replacements):
    raise NotImplementedError

def lattice_transform(structure, transform):
    transform = np.array(transform)
    if transform.shape == (3,3):
        print 'is a full lattice transform matrix'
    elif transform.shape in [ (1,3), (3,1) ]:
        transform = p.eye(3)*transform

    cell = np.dot(structure.cell, transform)
    raise NotImplementedError

def substitute(structure, replace, rescale=True):
    '''Replace atoms, as specified in a dict of pairs. 
    Optionally, can rescale the new volume to the total volume of the
    elemental phases of the new composition.

    Example:
    >>> s = Structure.create('POSCAR-Fe2O3')
    >>> s.substitute({'Fe':'Ni', 'O':'F'} rescale=True)
    '''

    struct = structure.copy()
    volume = 0.0
    for atom in struct:
        if atom.element_id in replace:
            atom.element_id = replace[atom.element_id]
        volume += atom.element.volume
    if rescale:
        struct.volume = volume
    struct.composition = Composition.get(struct.comp)
    return struct

