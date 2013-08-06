from qmpy.structure import Structure
from ase import Atoms

def to_ase(structure):
    atoms = Atoms(cell=structure.cell,
            scaled_positions=structure.scaled_coords, 
            magmoms=structure.magmoms,
            symbols=''.join(sorted(a.symbol for a in structure.atoms)))
    return atoms

def from_ase(atoms):
    struct = Structure()
    struct.cell = atoms.get_cell()
    for a in atoms: 
        atom = Atom()
        atom.symbol = a.symbol
        atom.x, atom.y, atom.z = a.position
        atom.direct = False
        struct.add_atom(atom)
    return struct
