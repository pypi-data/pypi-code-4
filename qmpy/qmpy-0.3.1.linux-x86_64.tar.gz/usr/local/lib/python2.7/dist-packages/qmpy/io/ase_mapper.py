#!/usr/bin/env python

'''
Interface to ASE Atoms, and Calculators.
'''

from qmpy.materials.structure import Structure
from qmpy.materials.atom import Atom

#try:
import ase
import ase.io
ASE_INSTALLED = True
#except ImportError:
#    ASE_INSTALLED = False
#    pass

def structure_to_atoms(structure):
    if not ASE_INSTALLED:
        print 'ASE must be installed to convert a Structure to an Atoms object'
        return
    atoms = Atoms(cell=structure.cell,
            scaled_positions=structure.scaled_coords, 
            magmoms=structure.magmoms,
            symbols=''.join(sorted(a.symbol for a in structure.atoms)))
    return atoms

def atoms_to_structure(atoms):
    if not ASE_INSTALLED:
        print 'ASE must be installed to convert Atoms object to a Structure'
        return
    struct = Structure()
    struct.cell = atoms.get_cell()
    for a in atoms: 
        atom = Atom()
        atom.symbol = a.symbol
        atom.coord = a.position
        atom.magmom = a.magmom
        atom.direct = False
        struct.add_atom(atom)
    return struct

def read_ase(filename):
    if not ASE_INSTALLED:
        print 'ASE must be installed to convert Atoms object to a Structure'
        return

    atoms = ase.io.read(filename)
    return atoms_to_structure(atoms)
