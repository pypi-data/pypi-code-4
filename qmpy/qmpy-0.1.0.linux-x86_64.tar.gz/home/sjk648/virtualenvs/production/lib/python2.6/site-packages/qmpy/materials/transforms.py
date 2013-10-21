import numpy as np

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

    struct = Structure()
    struct.cell = structure.cell
    volume = 0.0
    for a, coord in zip(structure.atoms, structure.scaled_coords):
        a2 = Atom()
        a2.forces = a.forces
        a2.coord = coord
        a2.direct = True
        if a.element_id in replace:
            a2.element_id = replace[a.element_id]
        else:
            a2.element_id = a.element_id
        struct.add_atom(a2) 
        volume += a2.element.volume
    if rescale:
        struct.volume = volume
    return struct

