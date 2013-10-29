#!/usr/bin/env python
# -*- coding: utf-8 -*-


from collections import defaultdict
import logging
import gzip
import os
from os.path import exists, isfile, isdir
import time

from django.db import models
import numpy as np

from qmpy.utils import *
import qmpy.materials.structure as st
import qmpy.materials.composition as comp
import qmpy.data.meta_data as ref

def write_poscar(struct, direct=True, distinct_by_ox=False):
    comp = struct.comp
    struct.atoms = atom_sort(struct.atoms)

    cdict = defaultdict(int)
    if not distinct_by_ox:
        ordered_keys = sorted(comp.keys())
        counts = [ int(comp[k]) for k in ordered_keys ]
    else:
        for a in struct.atoms:
            if int(a.oxidation_state) != a.oxidation_state:
                cdict['%s%+f' % (a.element_id, a.oxidation_state)] += 1
            else:
                cdict['%s%+d' % (a.element_id, a.oxidation_state)] += 1
        ordered_keys = sorted([ k for k in cdict.keys() ])
        counts = [ int(cdict[k]) for k in ordered_keys ]

    poscar = ' '.join(set(a.element_id for a in struct.atoms)) + '\n 1.0\n'
    cell = '\n'.join([ ' '.join([ '%f' % v  for v in vec ]) for vec in
        struct.cell ])
    poscar += cell +'\n'
    names = ' '.join( a for a in ordered_keys ) + '\n'
    ntypes = ' '.join( str(n) for n in counts ) + '\n'
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

def read_poscar(poscar):
    struct = st.Structure()
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
        struct.cell = cell
        struct.volume = -1*s

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

    struct.natoms = sum(counts)
    struct.ntypes = len(counts)
    composition = defaultdict(float)
    atoms = []
    inv = np.linalg.inv(cell).T
    for i in range(struct.natoms):
        atom = st.Atom()
        atom.element_id = atom_types[i]
        if direct:
            atom.coord = [ float(v) for v in poscar.readline().split() ]
        else:
            cart = [ float(v) for v in poscar.readline().split() ]
            atom.coord = np.dot(inv, cart)
        atom.direct = True
        atoms.append(atom)
        composition[atom_types[i]] += 1
    struct.atoms = atoms
    struct.composition = comp.Composition.get(composition)
    struct.reported_composition = comp.Composition.get(composition)
    return struct
