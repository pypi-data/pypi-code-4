from numpy.linalg import solve
import time
import copy
from collections import defaultdict

from qmpy.utils import *
from dev_qmpy.models.structure import Structure, Atom
from dev_qmpy.models.element import Element

def to_vasp(struct, direct=True):
    comp = struct.comp
    ordered_keys = sorted(comp.keys())
    atoms = sorted(struct.atoms, key=lambda x:x.element.symbol)
    poscar = ' '.join(set(a.symbol for a in atoms)) + '\n 1.0\n'
    cell = '\n'.join([ ' '.join([ '%f' % v  for v in vec ]) for vec in
        struct.cell ])
    poscar += cell +'\n'
    names = ' '.join( a for a in ordered_keys ) + '\n'
    ntypes = ' '.join( str(comp[k]) for k in ordered_keys ) + '\n'
    poscar += names
    poscar += ntypes
    if direct:
        poscar += 'direct\n'
        for x,y,z in struct.scaled_coords:
            poscar += ' %.10f %.10f %.10f\n' % (x,y,z)
    else:
        poscar += 'cartesian\n'
        for x, y, z in struct.coords:
            poscar += ' %.10f %.10f %.10f\n' % (x,y,z)
    return poscar

def from_vasp(poscar):
    struct = Structure()
    poscar = open(poscar,'r')
    title = poscar.readline().strip()
    scale = float(poscar.readline().strip())
    s = float(scale)
    cell = [[ float(v) for v in poscar.readline().split() ],
            [ float(v) for v in poscar.readline().split() ],
            [ float(v) for v in poscar.readline().split() ]]
    cell = np.array(cell)

    if s > 0:
        struct.cell = cell*s
    else:
        raise NotImplementedError, 'Not able to scale volume like this yet'

    vasp5 = False
    species = poscar.readline().strip().split()
    try:
        float(species[0])
    except:
        vasp5 = True
        counts = [ int(v) for v in poscar.readline().split() ]

    if not vasp5:
        species = title.strip().split()
        counts = species
        print 'Since not vasp5 format, title MUST be species present'

    atom_types = []
    for n,e in zip(counts, species):
        atom_types += [e]*n

    style = poscar.readline()
    direct = False
    if style[0] in ['D', 'd']:
        direct = True

    natoms = sum(counts)
    for i in range(natoms):
        atom = Atom()
        atom.element = Element.get(atom_types[i])
        atom.coord = [ float(v) for v in poscar.readline().split() ]
        atom.direct = direct
        struct.add_atom(atom)
    return struct

def to_incar(struct):
    incar = ''
    if any(a.magmom for a in struct.atoms):
        incar += ' ISPIN = 2\n'
        moms = [ a.magmom for a in struct.atoms ]
        magmoms = [[1, moms[0]]]
        for n in range(1, len(moms)):
            if moms[n] == moms[n-1]:
                magmoms[-1][0] += 1
            else:
                magmoms.append([1, moms[n]])
        momstr = ' '.join('%i*%.4f' % (v[0],v[1]) for v in magmoms)
        incar += ' MAGMOM = %s\n' %  momstr
    return incar
