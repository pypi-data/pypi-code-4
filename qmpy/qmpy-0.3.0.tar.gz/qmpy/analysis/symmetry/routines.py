'''
Useful symmetry functions.
'''

import qmpy.utils._spglib as spg
from qmpy.data import elements
import fractions as frac
import numpy as np

## spglib functions | http://spglib.sourceforge.net/

zdict = dict( (e['z'], e['symbol']) for e in elements.values() )

def find_structure_symmetry(structure, method='spglib',
        symprec=1e-5, angle_tolerance=-1.0):
    """
    Return the rotatiosn and translations which are possessed by the structure.
    
    Example:
    >>> from qmpy.io import read
    >>> from qmpy.analysis.symmetry import find_structure_symmetry
    >>> structure = read('POSCAR')
    >>> find_structure_symmetry(structure)
    
    """
    # Get number of symmetry operations and allocate symmetry operations
    multi = 48 * len(structure)
    rotation = np.zeros((multi, 3, 3), dtype='intc')
    translation = np.zeros((multi, 3))
  
    # Get symmetry operations
    magmoms = structure.magmoms
    if not any(magmoms):
        num_sym = spg.symmetry(rotation,
                               translation,
                               structure.cell.T.copy(),
                               structure.scaled_coords.copy(),
                               structure.atomic_numbers,
                               symprec,
                               angle_tolerance)
    else:
        num_sym = spg.symmetry_with_collinear_spin(rotation,
                                                   translation,
                                                   lattice,
                                                   positions,
                                                   numbers,
                                                   magmoms,
                                                   symprec,
                                                   angle_tolerance)
  
    return rotation[:num_sym], translation[:num_sym]

def get_symmetry_dataset(structure, symprec=1e-3, angle_tolerance=-1.0):
    """
    Return a full set of symmetry information from a given input structure.

    Mapping values:
        number: International space group number
        international: International symbol
        hall: Hall symbol
        transformation_matrix:
          Transformation matrix from lattice of input cell to Bravais lattice
          L^bravais = L^original * Tmat
        origin shift: Origin shift in the setting of 'Bravais lattice'
        rotations, translations:
          Rotation matrices and translation vectors
          Space group operations are obtained by
            [(r,t) for r, t in zip(rotations, translations)]
        wyckoffs:
          Wyckoff letters

    Example:
    >>> from qmpy.io import read
    >>> from qmpy.analysis.symmetry import get_symmetry_dataset
    >>> structure = read('POSCAR')
    >>> get_symmetry_dataset(structure)

    """
    keys = ('number',
            'international',
            'hall',
            'transformation_matrix',
            'origin_shift',
            'rotations',
            'translations',
            'wyckoffs',
            'equivalent_atoms')

    scaled = structure.site_coords.copy()
    labels = structure.site_labels.copy()
    ldict = dict( (k, i+1) for i, k in enumerate(list(set(labels))))
    numbers = np.array([ ldict[k] for k in labels ], dtype='intc')

    dataset = {}
    for key, data in zip(keys, 
            spg.dataset(
                structure.cell.T.copy(),
                scaled,
                numbers,
                symprec,
                angle_tolerance)):
        dataset[key] = data

    dataset['international'] = dataset['international'].strip()
    dataset['hall'] = dataset['hall'].strip()
    dataset['transformation_matrix'] = np.array(dataset['transformation_matrix']).T
    dataset['origin_shift'] = np.array(dataset['origin_shift'])
    dataset['rotations'] = np.array(dataset['rotations'])
    dataset['translations'] = np.array(dataset['translations'])
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    dataset['wyckoffs'] = [letters[x] for x in dataset['wyckoffs']]
    dataset['equivalent_atoms'] = np.array(dataset['equivalent_atoms'])

    return dataset

def get_spacegroup(structure, symprec=1e-5, angle_tolerance=-1.0):
    """
    Return space group in international table symbol and number
    as a string.
    """
    # Atomic positions have to be specified by scaled positions for spglib.
    return int(spg.spacegroup(structure.cell.T.copy(),
                          structure.scaled_coords.copy(),
                          structure.atomic_numbers,
                          symprec,
                          angle_tolerance).strip(' ()'))

def get_pointgroup(rotations):
    """
    Return point group in international table symbol and number.
    """

    # (symbol, pointgroup_number, transformation_matrix)
    return spg.pointgroup(rotations)

def refine_cell(structure, symprec=1e-5, angle_tolerance=-1.0):
    """
    Return refined cell
    """
    # Atomic positions have to be specified by scaled positions for spglib.
    num_atom = len(structure)
    lattice = structure.cell.T.copy()
    positions = np.zeros((num_atom * 4, 3), dtype='double')
    positions[:num_atom] = structure.scaled_coords.copy()

    numbers = np.zeros(num_atom * 4, dtype='intc')
    numbers[:num_atom] = structure.atomic_numbers.copy()
    num_atom_bravais = spg.refine_cell(lattice,
                                       positions,
                                       numbers,
                                       num_atom,
                                       symprec,
                                       angle_tolerance)

    positions %= 1.0
    positions %= 1.0

    if num_atom_bravais > 0:
        structure.cell = lattice.T
        structure.set_natoms(num_atom_bravais)
        for a, z, c in zip(structure.atoms,
                           numbers[:num_atom_bravais], 
                           positions[:num_atom_bravais]):
            a.element_id = zdict[z]
            a.coord = c
            a.direct = True
        return structure
    else:
        return structure


def find_primitive(structure, symprec=1e-5, angle_tolerance=-1.0):
    """
    A primitive cell in the input cell is searched and returned
    as an object of Atoms class.
    If no primitive cell is found, (None, None, None) is returned.
    """
    lattice = structure.cell.T.copy()
    positions = structure.scaled_coords.copy()
    numbers = structure.atomic_numbers.copy()

    num_atom_prim = spg.primitive(lattice,
                                  positions,
                                  numbers,
                                  symprec,
                                  angle_tolerance)
    positions %= 1.0
    positions %= 1.0
    if num_atom_prim > 0:
        structure.cell = lattice.T
        structure.set_natoms(num_atom_prim)
        for a, z, c in zip(structure.atoms,
                           numbers[:num_atom_prim], 
                           positions[:num_atom_prim]):
            a.element_id = zdict[z]
            a.coord = c
            a.direct = True
        return structure
    else:
        return structure

def equivalent_reflections(hkl, rotations):
    """Return all equivalent reflections to the list of Miller indices
    in hkl.

    Example:
    >>> equivalent_reflections([[0, 0, 2]], rotations)
    array([[ 0,  0, -2],
           [ 0, -2,  0],
           [-2,  0,  0],
           [ 2,  0,  0],
           [ 0,  2,  0],
           [ 0,  0,  2]])
    """
    hkl = np.array(hkl, dtype='intc', ndmin=2)
    n, nrot = len(hkl), len(rotations)
    R = rotations.transpose(0, 2, 1).reshape((3*nrot, 3)).T
    refl = np.dot(hkl, R).reshape((n*nrot, 3))
    ind = np.lexsort(refl.T)
    refl = refl[ind]
    diff = np.diff(refl, axis=0)
    mask = np.any(diff, axis=1)
    return np.vstack((refl[mask], refl[-1,:]))

def normalised_reflections(hkl, rotations):
    """Returns an array of same size as *hkl*, containing the
    corresponding symmetry-equivalent reflections of lowest
    indices.

    Example:
    >>> sg.symmetry_normalised_reflections([[2, 0, 0], [0, 2, 0]])
    array([[ 0,  0, -2],
           [ 0,  0, -2]])
    """
    hkl = np.array(hkl, dtype='intc', ndmin=2)
    normalised = np.empty(hkl.shape, int)
    R = rotations.transpose(0, 2, 1)
    for i, g in enumerate(hkl):
        gsym = np.dot(R, g)
        j = np.lexsort(gsym.T)[0]
        normalised[i,:] = gsym[j]
    return normalised

def parse_sitesym(sitesym, sep=','):
    rot = np.zeros((3, 3), dtype='intc')
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
